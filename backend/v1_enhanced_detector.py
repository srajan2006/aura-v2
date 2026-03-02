import cv2
import numpy as np
import json
from PIL import Image
from collections import Counter
from sklearn.cluster import KMeans
import tensorflow as tf
from tensorflow import keras
from pathlib import Path

class V1EnhancedDetector:
    
    def __init__(self):
        # Load model
        model_path = Path("aura_garment_model.h5")
        labels_path = Path("class_names.json")
        
        if model_path.exists():
            try:
                self.model = keras.models.load_model(str(model_path))
                print("✅ V1 Model loaded successfully!")
                self.model_loaded = True
                input_shape = self.model.input_shape
                self.target_size = (input_shape[1], input_shape[2])
                print(f"✅ Model input size: {self.target_size}")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                self.model_loaded = False
                self.target_size = (224, 224)
        else:
            print("❌ Model file not found.")
            self.model_loaded = False
            self.target_size = (224, 224)
        
        if labels_path.exists():
            with open(labels_path, 'r') as f:
                self.garment_labels = json.load(f)
                print(f"✅ Labels loaded: {self.garment_labels}")
        else:
            self.garment_labels = ['jacket', 'jeans', 'shirt', 'tshirt']
            print(f"⚠️ Using default labels")
        
        # Color palette (kept for reference, HSV logic used in detection)
        self.color_names = {
            'black': (20, 20, 20),
            'darkgrey': (70, 70, 70),
            'grey': (128, 128, 128),
            'lightgrey': (180, 180, 180),
            'white': (235, 235, 235),
            'red': (200, 30, 30),
            'orange': (240, 110, 30),
            'yellow': (230, 210, 40),
            'green': (40, 150, 40),
            'lightgreen': (120, 200, 120),
            'blue': (30, 80, 180),
            'lightblue': (100, 150, 200),
            'skyblue': (135, 185, 220),
            'navy': (20, 40, 80),
            'purple': (120, 50, 150),
            'pink': (240, 140, 170),
            'brown': (100, 50, 20),
            'tan': (180, 140, 100),
            'beige': (210, 190, 160),
            'khaki': (170, 160, 110),
            'cream': (245, 235, 210),
        }
    
    def preprocess_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize(self.target_size)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_array = np.array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array.astype('float32')
            return img_array
        except Exception as e:
            print(f"Error preprocessing: {e}")
            return None
    
    def detect_garment_type(self, image_path):
        if not self.model_loaded:
            return self._fallback_detection(image_path)
        
        try:
            img_array = self.preprocess_image(image_path)
            if img_array is None:
                return "tshirt"
            
            predictions = self.model.predict(img_array, verbose=0)
            predicted_class = np.argmax(predictions[0])
            confidence = predictions[0][predicted_class]
            garment_type = self.garment_labels[predicted_class]
            
            print(f"🎯 Garment: {garment_type} ({confidence:.2%})")
            return garment_type
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._fallback_detection(image_path)
    
    def _fallback_detection(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return "tshirt"
        height, width = img.shape[:2]
        aspect_ratio = height / width
        if aspect_ratio > 1.4:
            return "jeans"
        elif aspect_ratio < 0.9:
            return "jacket"
        else:
            return "tshirt"
    
    def detect_dominant_color(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                return "grey", False
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (200, 200))
            pixels = img.reshape(-1, 3)
            
            # FIX 1: Much better background removal
            # Remove pure black, pure white backgrounds, AND grey/neutral backgrounds
            mask = (
                ~(np.all(pixels < 50, axis=1)) &            # remove black
                ~(np.all(pixels > 220, axis=1)) &            # remove white background
                ~(                                            # remove grey backgrounds
                    (np.max(pixels, axis=1).astype(int) - np.min(pixels, axis=1).astype(int) < 20) &
                    (pixels[:, 0] > 160)
                )
            )
            pixels = pixels[mask]
            
            if len(pixels) < 100:
                return "grey", False
            
            # Use 5 clusters for better color separation
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_
            labels = kmeans.labels_
            counts = Counter(labels)
            
            sorted_indices = sorted(counts, key=counts.get, reverse=True)
            sorted_colors = [colors[i] for i in sorted_indices]
            percentages = [counts[i]/len(labels) for i in sorted_indices]
            
            print(f"🎨 Top colors:")
            for i in range(min(5, len(sorted_colors))):
                rgb = tuple(sorted_colors[i].astype(int))
                pct = percentages[i] * 100
                name = self._get_color_name(sorted_colors[i])
                print(f"   {rgb} = {name} ({pct:.0f}%)")
            
            # FIX 2: Raise multicolor threshold from 15% → 30%
            # AND require colors to be genuinely different (not just shadows)
            is_multicolor = False
            if len(percentages) >= 2 and percentages[1] > 0.30:
                color1 = sorted_colors[0]
                color2 = sorted_colors[1]
                color_distance = np.sqrt(sum((float(color1[i]) - float(color2[i]))**2 for i in range(3)))
                if color_distance > 60:  # Must be genuinely different colors
                    is_multicolor = True
            
            color_name = self._get_color_name(sorted_colors[0])
            
            print(f"✅ Color: {color_name} (multi: {is_multicolor})")
            return color_name, is_multicolor
            
        except Exception as e:
            print(f"❌ Color error: {e}")
            return "grey", False
    
    def _get_color_name(self, rgb):
        # HSV-based color naming with fixed dark color handling
        rgb_pixel = np.uint8([[list(rgb)]])
        hsv = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2HSV)[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

        # Step 1: Very dark pixels = black regardless of hue
        # Fixes black jeans/tshirts being called navy or red
        if v < 50:
            return 'black'

        # Step 2: Low saturation = achromatic
        if s < 40:
            if v < 100:  return 'darkgrey'
            if v < 160:  return 'grey'
            if v < 210:  return 'lightgrey'
            return 'white'

        # Step 3: Dark but saturated
        if v < 80:
            if s > 80 and 100 < h < 135:  return 'navy'
            if h < 15 or h > 160:          return 'brown'
            return 'darkgrey'

        # Step 4: Chromatic colors by hue
        if h < 10 or h > 170:  return 'red'
        if h < 20:             return 'orange'
        if h < 35:             return 'brown' if s > 150 else 'tan'
        if h < 45:             return 'yellow'
        if h < 75:             return 'green'
        if h < 85:             return 'lightgreen'
        if h < 100:            return 'skyblue'
        if h < 110:            return 'lightblue'
        if h < 125:            return 'blue'
        if h < 135:            return 'navy'
        if h < 150:            return 'purple'
        if h < 165:            return 'pink'

        return 'grey'
    
    def detect_pattern(self, image_path):
        try:
            gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                return "solid"
            
            gray = cv2.resize(gray, (400, 400))
            
            # FIX 4: Focus on center crop to avoid background edges
            h, w = gray.shape
            center = gray[h//6:5*h//6, w//6:5*w//6]
            
            variance = np.var(center)
            
            # Higher Canny thresholds = less noise detected as edges
            edges = cv2.Canny(center, 80, 200)
            edge_density = np.count_nonzero(edges) / edges.size
            
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            h_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, h_kernel)
            v_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, v_kernel)
            
            h_count = np.count_nonzero(h_lines)
            v_count = np.count_nonzero(v_lines)
            
            print(f"📐 Pattern: var={variance:.0f}, edges={edge_density:.3f}, h={h_count}, v={v_count}")
            
            # FIX 5: Much stricter thresholds — old ones caused everything to be "printed"
            if h_count > 500 and v_count > 500:
                return "checked"
            elif h_count > 600 or v_count > 600:
                return "striped"
            elif variance > 4500 and edge_density > 0.18:  # BOTH must be high (was OR)
                return "printed"
            else:
                return "solid"
                
        except Exception as e:
            print(f"❌ Pattern error: {e}")
            return "solid"
    
    def analyze_garment(self, image_path):
        print(f"\n🔍 Analyzing: {image_path}")
        
        garment_type = self.detect_garment_type(image_path)
        color, is_multicolor = self.detect_dominant_color(image_path)
        pattern = self.detect_pattern(image_path)
        
        color_desc = f"multicolor-{color}" if is_multicolor else color
        full_desc = f"{pattern} {color_desc} {garment_type}"
        
        result = {
            "garment_type": garment_type,
            "color": color,
            "is_multicolor": is_multicolor,
            "pattern": pattern,
            "color_description": color_desc,
            "full_description": full_desc,
            "confidence": "high"
        }
        
        print(f"✅ Final: {full_desc}\n")
        return result


# Singleton instance imported by main.py
v1_detector = V1EnhancedDetector()