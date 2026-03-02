import random
from collections import defaultdict
from typing import List, Dict, Tuple

class OutfitRecommender:
    """
    Smart outfit recommendation system
    Suggests complete outfits based on color harmony and garment types
    """
    
    def __init__(self):
        # Color harmony rules (what colors go well together)
        self.color_harmony = {
            'black': ['white', 'grey', 'red', 'blue', 'yellow', 'orange', 'pink', 'purple', 'green'],
            'white': ['black', 'navy', 'blue', 'red', 'green', 'brown', 'grey', 'pink', 'purple'],
            'grey': ['black', 'white', 'blue', 'navy', 'pink', 'purple', 'yellow', 'red'],
            'navy': ['white', 'beige', 'cream', 'brown', 'grey', 'red', 'pink'],
            'blue': ['white', 'black', 'brown', 'beige', 'grey', 'yellow', 'orange'],
            'lightblue': ['white', 'navy', 'brown', 'beige', 'grey', 'pink'],
            'red': ['black', 'white', 'grey', 'navy', 'beige', 'cream'],
            'orange': ['blue', 'navy', 'brown', 'beige', 'white', 'black'],
            'yellow': ['grey', 'black', 'blue', 'navy', 'white', 'brown'],
            'green': ['brown', 'beige', 'cream', 'white', 'black', 'grey'],
            'purple': ['grey', 'white', 'black', 'beige', 'pink'],
            'pink': ['grey', 'white', 'navy', 'black', 'blue'],
            'brown': ['beige', 'cream', 'white', 'blue', 'green', 'orange'],
            'beige': ['brown', 'navy', 'blue', 'white', 'green', 'red'],
            'khaki': ['brown', 'navy', 'white', 'blue', 'green'],
            'cream': ['brown', 'navy', 'green', 'red', 'blue'],
        }
        
        # Garment type categories
        self.upper_body = ['shirt', 'tshirt', 'jacket']
        self.lower_body = ['jeans', 'trousers', 'shorts']
        self.outerwear = ['jacket', 'blazer', 'coat']
    
    def get_recommendations(self, wardrobe_items: List[Dict], max_outfits: int = 5, shuffle: bool = True) -> List[Dict]:
        """
        Generate outfit recommendations from wardrobe items
        
        Args:
            wardrobe_items: List of wardrobe items with garment_type, color, etc.
            max_outfits: Maximum number of outfit suggestions
            shuffle: Randomize results for variety
            
        Returns:
            List of recommended outfits with items and reasoning
        """
        # Organize items by type
        items_by_type = defaultdict(list)
        for item in wardrobe_items:
            garment_type = item.get('garment_type', '').lower()
            items_by_type[garment_type].append(item)
        
        # Separate upper and lower body items
        upper_items = []
        lower_items = []
        
        for item_type in self.upper_body:
            upper_items.extend(items_by_type.get(item_type, []))
        
        for item_type in self.lower_body:
            lower_items.extend(items_by_type.get(item_type, []))
        
        # Generate outfit combinations
        outfits = []
        
        # Try all combinations of upper + lower
        for upper in upper_items:
            for lower in lower_items:
                outfit = self._create_outfit(upper, lower)
                if outfit:
                    outfits.append(outfit)
        
        # Sort by score
        outfits.sort(key=lambda x: x['score'], reverse=True)
        
        # Shuffle for variety if requested (keeps top-rated but randomizes order)
        if shuffle and len(outfits) > max_outfits:
            # Keep top 50% by score, randomize the selection
            top_count = max(max_outfits * 2, len(outfits) // 2)
            top_outfits = outfits[:top_count]
            random.shuffle(top_outfits)
            return top_outfits[:max_outfits]
        
        # Return top recommendations
        return outfits[:max_outfits]
    
    def _create_outfit(self, upper: Dict, lower: Dict) -> Dict:
        """
        Create an outfit from upper and lower garments
        Calculate compatibility score
        """
        upper_color = self._normalize_color(upper.get('color', 'grey'))
        lower_color = self._normalize_color(lower.get('color', 'grey'))
        
        # Calculate color compatibility score (0-100)
        color_score = self._calculate_color_score(upper_color, lower_color)
        
        # Calculate pattern compatibility
        pattern_score = self._calculate_pattern_score(
            upper.get('pattern', 'solid'),
            lower.get('pattern', 'solid')
        )
        
        # Overall score (weighted average)
        total_score = (color_score * 0.6) + (pattern_score * 0.4)
        
        # Generate style reasoning
        reasoning = self._generate_reasoning(
            upper, lower, upper_color, lower_color, total_score
        )
        
        # Determine style
        style = self._determine_style(upper, lower)
        
        outfit = {
            'items': [upper, lower],
            'upper': upper,
            'lower': lower,
            'score': round(total_score, 1),
            'color_score': round(color_score, 1),
            'pattern_score': round(pattern_score, 1),
            'style': style,
            'reasoning': reasoning,
            'color_harmony': color_score >= 70
        }
        
        return outfit
    
    def _normalize_color(self, color: str) -> str:
        """Normalize color names for matching"""
        color = color.lower().strip()
        
        # Handle multicolor
        if 'multicolor' in color:
            # Extract primary color after 'multicolor-'
            if '-' in color:
                color = color.split('-')[1]
        
        # Map similar colors
        color_map = {
            'lightgrey': 'grey',
            'darkgrey': 'grey',
            'skyblue': 'lightblue',
            'darkgreen': 'green',
            'tan': 'brown',
            'coral': 'orange',
            'cream': 'beige',
        }
        
        return color_map.get(color, color)
    
    def _calculate_color_score(self, color1: str, color2: str) -> float:
        """
        Calculate how well two colors go together (0-100)
        """
        # Same color = good but not perfect (avoid monotone)
        if color1 == color2:
            return 75.0
        
        # Check color harmony rules
        harmonious_colors = self.color_harmony.get(color1, [])
        
        if color2 in harmonious_colors:
            return 95.0  # Great match!
        
        # Neutral colors go with most things
        neutrals = ['black', 'white', 'grey', 'beige', 'cream']
        if color1 in neutrals or color2 in neutrals:
            return 80.0
        
        # Otherwise, mediocre match
        return 50.0
    
    def _calculate_pattern_score(self, pattern1: str, pattern2: str) -> float:
        """
        Calculate pattern compatibility (0-100)
        """
        # Both solid = safe and good
        if pattern1 == 'solid' and pattern2 == 'solid':
            return 90.0
        
        # One solid, one pattern = excellent
        if (pattern1 == 'solid') != (pattern2 == 'solid'):
            return 100.0
        
        # Both patterned = risky but can work
        if pattern1 == pattern2:
            return 60.0  # Same pattern type
        else:
            return 40.0  # Different patterns (checked + striped = clash)
    
    def _determine_style(self, upper: Dict, lower: Dict) -> str:
        """Determine the overall style of the outfit"""
        upper_type = upper.get('garment_type', '').lower()
        lower_type = lower.get('garment_type', '').lower()
        
        # Formal
        if upper_type == 'shirt' and lower_type in ['trousers', 'jeans']:
            return 'smart-casual'
        
        # Casual
        if upper_type == 'tshirt':
            return 'casual'
        
        # Sporty
        if lower_type == 'shorts':
            return 'sporty'
        
        # Default
        return 'everyday'
    
    def _generate_reasoning(self, upper: Dict, lower: Dict, 
                          upper_color: str, lower_color: str, score: float) -> str:
        """Generate human-readable reasoning for the outfit"""
        
        reasons = []
        
        # Color reasoning
        if score >= 85:
            if upper_color == lower_color:
                reasons.append(f"Monochrome {upper_color} look creates a sleek appearance")
            else:
                reasons.append(f"{upper_color.capitalize()} and {lower_color} are a classic combination")
        elif score >= 70:
            reasons.append(f"{upper_color.capitalize()} pairs well with {lower_color}")
        else:
            reasons.append("Color combination is bold and experimental")
        
        # Pattern reasoning
        upper_pattern = upper.get('pattern', 'solid')
        lower_pattern = lower.get('pattern', 'solid')
        
        if upper_pattern != 'solid' and lower_pattern == 'solid':
            reasons.append(f"{upper_pattern.capitalize()} top balanced with solid bottom")
        elif upper_pattern == 'solid' and lower_pattern != 'solid':
            reasons.append(f"Solid top balances {lower_pattern} bottom")
        elif upper_pattern == 'solid' and lower_pattern == 'solid':
            reasons.append("Clean, minimalist look")
        
        # Style reasoning
        style = self._determine_style(upper, lower)
        style_desc = {
            'smart-casual': 'Perfect for work or semi-formal occasions',
            'casual': 'Great for everyday wear and relaxed settings',
            'sporty': 'Ideal for active days or weekend activities',
            'everyday': 'Versatile outfit for any occasion'
        }
        reasons.append(style_desc.get(style, 'Versatile and practical'))
        
        return '. '.join(reasons) + '.'

# Global instance
recommender = OutfitRecommender()