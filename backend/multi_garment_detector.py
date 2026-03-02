import cv2
import numpy as np
from PIL import Image
from collections import Counter
from sklearn.cluster import KMeans

class MultiGarmentDetector:
    """
    Detect multiple garments in a single image (only when they exist)
    """
    
    def __init__(self):
        # Color palette
        self.color_names = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'brown': (165, 42, 42),
            'grey': (128, 128, 128),
            'navy': (0, 0, 128),
            'beige': (245, 245, 220),
            'maroon': (128, 0, 0),
            'olive': (128, 128, 0),
            'cream': (255, 253, 208)
        }
    
    def has_significant_content(self, region_img):
        """
        Check if region has actual garment content (not just background)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
        
        # Calculate variance (low variance = likely empty/background)
        variance = np.var(gray)
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        # Check for actual content
        # Empty regions have: very low variance, extreme brightness, or no edges
        is_empty = (
            variance < 200 or  # Too uniform
            mean_brightness > 240 or  # Too bright (white background)
            mean_brightness < 15 or  # Too dark (black background)
            edge_density < 0.01  # No structure
        )
        
        return not is_empty
    
    def detect_regions(self, image_path):
        """
        Detect different regions and check if they have content
        """
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        height, width = img.shape[:2]
        regions = []
        
        # Upper region (top 55% of image) - for shirts/tshirts/jackets
        upper_box = (0, 0, width, int(height * 0.55))
        upper_img = img[0:int(height * 0.55), :]
        
        if self.has_significant_content(upper_img):
            regions.append({
                'box': upper_box,
                'image': upper_img,
                'category': 'upper'
            })
        
        # Lower region (bottom 55% from 45% down) - for pants/jeans
        lower_box = (0, int(height * 0.45), width, height)
        lower_img = img[int(height * 0.45):, :]
        
        if self.has_significant_content(lower_img):
            regions.append({
                'box': lower_box,
                'image': lower_img,
                'category': 'lower'
            })
        
        return regions
    
    def classify_garment_region(self, region_img, category, full_img_aspect):
        """
        Classify garment type in region
        """
        height, width = region_img.shape[:2]
        aspect_ratio = height / width
        
        gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
        
        if category == 'upper':
            # Check for collar
            top_section = region_img[0:int(height*0.2), :]
            middle_section = region_img[int(height*0.2):int(height*0.6), :]
            
            top_brightness = np.mean(cv2.cvtColor(top_section, cv2.COLOR_BGR2GRAY))
            middle_brightness = np.mean(cv2.cvtColor(middle_section, cv2.COLOR_BGR2GRAY))
            
            has_collar = abs(top_brightness - middle_brightness) > 12
            
            # Check if image is wide (likely jacket)
            if full_img_aspect < 1.0:  # Wider than tall
                return "jacket"
            elif has_collar:
                return "shirt"
            else:
                return "tshirt"
        
        elif category == 'lower':
            # For lower garments
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.count_nonzero(edges) / edges.size
            
            # Jeans typically have more texture/edges
            if edge_density > 0.05 or aspect_ratio > 0.8:
                return "jeans"
            else:
                return "trousers"
        
        return None
    
    def detect_color_in_region(self, region_img):
        """
        Detect dominant color in region
        """
        try:
            img_rgb = cv2.cvtColor(region_img, cv2.COLOR_BGR2RGB)
            img_rgb = cv2.resize(img_rgb, (100, 100))
            
            pixels = img_rgb.reshape(-1, 3)
            
            # Remove extreme values
            mask = np.all(pixels > 25, axis=1) & np.all(pixels < 235, axis=1)
            pixels = pixels[mask]
            
            if len(pixels) < 10:
                return "grey", False
            
            kmeans = KMeans(n_clusters=min(3, len(pixels)), random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_
            labels = kmeans.labels_
            counts = Counter(labels)
            
            sorted_colors = [colors[i] for i in sorted(counts, key=counts.get, reverse=True)]
            color_percentages = [counts[i]/len(labels) for i in sorted(counts, key=counts.get, reverse=True)]
            
            is_multicolor = len([p for p in color_percentages if p > 0.2]) >= 2
            
            primary_rgb = sorted_colors[0]
            color_name = self._get_color_name(primary_rgb)
            
            return color_name, is_multicolor
            
        except Exception as e:
            print(f"Color detection error: {e}")
            return "grey", False
    
    def _get_color_name(self, rgb):
        """Map RGB to color name"""
        min_distance = float('inf')
        closest_color = 'grey'
        
        for name, color_rgb in self.color_names.items():
            distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, color_rgb)))
            if distance < min_distance:
                min_distance = distance
                closest_color = name
        
        return closest_color
    
    def detect_pattern_in_region(self, region_img):
        """
        Detect pattern in region
        """
        try:
            gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (150, 150))
            
            variance = np.var(gray)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.count_nonzero(edges) / edges.size
            
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
            
            h_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            v_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            h_count = np.count_nonzero(h_lines)
            v_count = np.count_nonzero(v_lines)
            
            if h_count > 80 and v_count > 80:
                return "checked"
            elif h_count > 100 or v_count > 100:
                return "striped"
            elif edge_density > 0.12 or variance > 1200:
                return "printed"
            else:
                return "solid"
                
        except:
            return "solid"
    
    def analyze_multi_garment(self, image_path):
        """
        Analyze image and detect ALL garments present
        Only returns garments that actually exist in the image
        """
        # Load full image to get overall aspect ratio
        full_img = cv2.imread(image_path)
        if full_img is None:
            return []
        
        full_height, full_width = full_img.shape[:2]
        full_aspect_ratio = full_height / full_width
        
        # Detect regions with actual content
        regions = self.detect_regions(image_path)
        
        detected_garments = []
        
        for region in regions:
            region_img = region['image']
            category = region['category']
            
            if region_img.size == 0:
                continue
            
            # Classify garment type
            garment_type = self.classify_garment_region(region_img, category, full_aspect_ratio)
            
            if garment_type is None:
                continue
            
            # Detect color
            color, is_multicolor = self.detect_color_in_region(region_img)
            
            # Detect pattern
            pattern = self.detect_pattern_in_region(region_img)
            
            # Build description
            color_desc = f"multicolor-{color}" if is_multicolor else color
            
            garment_data = {
                "garment_type": garment_type,
                "color": color,
                "is_multicolor": is_multicolor,
                "pattern": pattern,
                "color_description": color_desc,
                "category": category,
                "full_description": f"{pattern} {color_desc} {garment_type}"
            }
            
            detected_garments.append(garment_data)
        
        # If nothing detected, return single generic item
        if len(detected_garments) == 0:
            # Fallback - analyze full image as single garment
            color, is_multicolor = self.detect_color_in_region(full_img)
            pattern = self.detect_pattern_in_region(full_img)
            
            # Guess type from aspect ratio
            if full_aspect_ratio > 1.4:
                garment_type = "jeans"
            elif full_aspect_ratio < 0.9:
                garment_type = "jacket"
            else:
                garment_type = "tshirt"
            
            color_desc = f"multicolor-{color}" if is_multicolor else color
            
            detected_garments.append({
                "garment_type": garment_type,
                "color": color,
                "is_multicolor": is_multicolor,
                "pattern": pattern,
                "color_description": color_desc,
                "category": "full",
                "full_description": f"{pattern} {color_desc} {garment_type}"
            })
        
        return detected_garments

# Global instance
multi_detector = MultiGarmentDetector()