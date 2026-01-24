from typing import List, Dict, Any, Tuple, Optional
import random
from src.story_inspired_puzzles.utils import clean_and_split_word

class CrosswordGenerator:
    def __init__(self):
        self.grid = {}  # (x, y) -> akshara_string
        self.placed_words = []
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

    def generate_layout(self, word_list: List[Dict[str, str]], grid_size: int = 20, attempts: int = 20) -> Dict[str, Any]:
        """
        Takes a list of dicts.
        Returns a layout with Disjoint Clusters packed efficiently.
        Rule: Each cluster must have at least 3 words.
        Constraint: Minimize area (Compactness).
        """
        # 1. Clean words
        clean_words = []
        for w in word_list:
            original = w['answer']
            aksharas = clean_and_split_word(original)
            if len(aksharas) > 1:
                clean_words.append({
                    'original_data': w,
                    'clean_word': aksharas, 
                    'length': len(aksharas),
                    'id': original
                })

        if not clean_words:
            return None
        
        best_layout = None
        best_word_count = -1
        min_total_area = float('inf')
        
        # Try multiple cluster seeds
        for _ in range(attempts):
            import copy
            words_pool = copy.deepcopy(clean_words)
            random.shuffle(words_pool)
            
            # Phase 1: Form Clusters (Greedy Growth)
            clusters = [] 
            
            while words_pool:
                # Start new cluster with longest remaining word
                words_pool.sort(key=lambda x: x['length'], reverse=True)
                seed = words_pool.pop(0)
                
                cluster_grid = {}
                cluster_placed = []
                
                # Place seed at 0,0 across
                self._place_word_in_dict(seed, 0, 0, 'across', cluster_grid, cluster_placed)
                
                # Grow cluster
                added_something = True
                while added_something:
                    added_something = False
                    to_remove_indices = []
                    
                    for i, w in enumerate(words_pool):
                        res = self._try_fit_in_cluster(w, cluster_grid)
                        if res:
                            self._place_word_in_dict(w, res[0], res[1], res[2], cluster_grid, cluster_placed)
                            to_remove_indices.append(i)
                            added_something = True
                            break 
                    
                    for i in sorted(to_remove_indices, reverse=True):
                        words_pool.pop(i)
                    
                # Cluster finished. Check size.
                if len(cluster_placed) >= 3:
                     clusters.append({
                         'grid': cluster_grid,
                         'words': cluster_placed
                     })
            
            # Phase 2: Pack Clusters (Bin Packing - Best Fit Area + Rotation)
            if not clusters:
                continue

            # Calculate bounds/area for sorting
            for c in clusters:
                self._enrich_cluster_bounds(c)
            
            # Sort largest area first
            clusters.sort(key=lambda x: x['area'], reverse=True)
            
            master_grid = {}
            master_placed = []
            
            # Place first cluster at 0,0
            first_c = clusters[0]
            ox = -int(first_c['w'] / 2)
            oy = -int(first_c['h'] / 2)
            self._merge_cluster(first_c, ox, oy, master_grid, master_placed)
            
            for c in clusters[1:]:
                # Try placing 'c' AND 'c_rotated'
                # Find best spot overall
                
                c_rot = self._transpose_cluster(c)
                self._enrich_cluster_bounds(c_rot)
                
                candidates = [c, c_rot]
                best_variant_spot = None # (cluster_variant, x, y)
                best_variant_score = (float('inf'), float('inf')) # (Area, Dist)
                
                mb_min_x, mb_max_x, mb_min_y, mb_max_y = self._get_bounds(master_grid)
                center_x = (mb_min_x + mb_max_x) // 2
                center_y = (mb_min_y + mb_max_y) // 2
                
                # Search loop
                search_limit = 60
                
                for r in range(0, search_limit, 2):
                    found_in_ring = False
                    
                    for variant in candidates:
                        # Optimization: if current best is area=0 (impossible), keep searching
                        # If we found a good fit in previous ring, we might skip checking this variant if its dims are huge? No.
                        
                        limit_r_check = max(variant['w'], variant['h']) + r + 5 # Dynamic limit based on r roughly? 
                        
                        for x in range(center_x - r, center_x + r + 1, 2):
                            for y in range(center_y - r, center_y + r + 1, 2):
                                if abs(x - center_x) != r and abs(y - center_y) != r: continue
                                
                                if self._can_place_cluster(variant, x, y, master_grid):
                                    # Calc Metric
                                    nb_min_x = min(mb_min_x, x + variant['bounds'][0])
                                    nb_max_x = max(mb_max_x, x + variant['bounds'][1])
                                    nb_min_y = min(mb_min_y, y + variant['bounds'][2])
                                    nb_max_y = max(mb_max_y, y + variant['bounds'][3])
                                    
                                    new_area = (nb_max_x - nb_min_x) * (nb_max_y - nb_min_y)
                                    dist = abs(x) + abs(y)
                                    
                                    score = (new_area, dist)
                                    if score < best_variant_score:
                                        best_variant_score = score
                                        best_variant_spot = (variant, x, y)
                                    
                                    found_in_ring = True
                    
                    if found_in_ring and best_variant_spot:
                        # We found something in this ring. 
                        # To ensure GLOBAL best in this expanding wavefront, we finish the ring.
                        # Maybe break outer loop? 
                        # Yes, generally first ring hit is best for compactness.
                        break
                
                if best_variant_spot:
                    win_c, wx, wy = best_variant_spot
                    self._merge_cluster(win_c, wx, wy, master_grid, master_placed)
                
            
            # Score this attempt
            count = len(master_placed)
            
            # Calculate final area
            fb = self._get_bounds(master_grid)
            final_area = (fb[1]-fb[0]) * (fb[3]-fb[2])
            
            # Priority: 1. Count (Must be max), 2. Area (Must be min)
            if count > best_word_count:
                best_word_count = count
                min_total_area = final_area
                best_layout = self._build_result(master_grid, master_placed, len(clean_words))
            elif count == best_word_count:
                if final_area < min_total_area:
                    min_total_area = final_area
                    best_layout = self._build_result(master_grid, master_placed, len(clean_words))
            
            if best_word_count >= len(clean_words) and attempts > 5:  
                # If we got all words, maybe continue to find tighter packing?
                # But speed matters.
                pass
                
        return best_layout

    def _transpose_cluster(self, cluster):
        # Swap x,y and directions
        import copy
        new_c = { 'grid': {}, 'words': [] }
        
        # Transpose Grid: (x,y) -> (y,x)
        for (x,y), char in cluster['grid'].items():
            new_c['grid'][(y,x)] = char
            
        # Transpose Words
        for w in cluster['words']:
            nw = copy.deepcopy(w)
            nw['x'], nw['y'] = w['y'], w['x']
            nw['direction'] = 'down' if w['direction'] == 'across' else 'across'
            new_c['words'].append(nw)
            
        return new_c

    def _enrich_cluster_bounds(self, c):
        c['bounds'] = self._get_bounds(c['grid']) 
        c['w'] = c['bounds'][1] - c['bounds'][0] + 1
        c['h'] = c['bounds'][3] - c['bounds'][2] + 1
        c['area'] = c['w'] * c['h']

    def _place_word_in_dict(self, word_obj, x, y, direction, grid, placed_list):
        word = word_obj['clean_word']
        for i, char in enumerate(word):
            cx, cy = (x + i, y) if direction == 'across' else (x, y + i)
            grid[(cx, cy)] = char
        import copy
        w_copy = copy.deepcopy(word_obj)
        w_copy['x'] = x
        w_copy['y'] = y
        w_copy['direction'] = direction
        placed_list.append(w_copy)

    def _try_fit_in_cluster(self, word_obj, grid):
        word = word_obj['clean_word']
        potential = []
        for i, char in enumerate(word):
            for (gx, gy), gchar in grid.items():
                if gchar == char:
                    sx, sy = gx - i, gy
                    if self._check_word_fit(word, sx, sy, 'across', grid):
                        potential.append((sx, sy, 'across'))
                    sx, sy = gx, gy - i
                    if self._check_word_fit(word, sx, sy, 'down', grid):
                        potential.append((sx, sy, 'down'))
        if not potential: return None
        return random.choice(potential)

    def _check_word_fit(self, word, sx, sy, direction, grid):
        for i, char in enumerate(word):
            cx, cy = (sx + i, sy) if direction == 'across' else (sx, sy + i)
            if (cx, cy) in grid:
                if grid[(cx, cy)] != char: return False
            else:
                if direction == 'across':
                    neighbors = [(cx, cy-1), (cx, cy+1)]
                else:
                    neighbors = [(cx-1, cy), (cx+1, cy)]
                for nx, ny in neighbors:
                    if (nx, ny) in grid: return False
        bx, by = (sx - 1, sy) if direction == 'across' else (sx, sy - 1)
        if (bx, by) in grid: return False
        ex, ey = (sx + len(word), sy) if direction == 'across' else (sx, sy + len(word))
        if (ex, ey) in grid: return False
        return True

    def _get_bounds(self, grid):
        if not grid: return (0,0,0,0)
        xs = [k[0] for k in grid]
        ys = [k[1] for k in grid]
        return (min(xs), max(xs), min(ys), max(ys))

    def _can_place_cluster(self, cluster, ox, oy, master_grid):
        grid = cluster['grid']
        for (cx, cy) in grid:
            mx, my = cx + ox, cy + oy
            check_points = [
                (mx, my), (mx+1, my), (mx-1, my), (mx, my+1), (mx, my-1),
                (mx+1, my+1), (mx-1, my-1), (mx+1, my-1), (mx-1, my+1) 
            ]
            for p in check_points:
                if p in master_grid: return False
        return True

    def _merge_cluster(self, cluster, ox, oy, master_grid, master_placed):
        for (cx, cy), char in cluster['grid'].items():
            master_grid[(cx + ox, cy + oy)] = char
        for w in cluster['words']:
            import copy
            nw = copy.deepcopy(w)
            nw['x'] += ox
            nw['y'] += oy
            master_placed.append(nw)

    def _build_result(self, grid, placed_words, total_input_count):
        if not grid: return None
        xs = [x for x, y in grid.keys()]
        ys = [y for x, y in grid.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        final_words = []
        for pw in placed_words:
            final_words.append({
                'answer': pw['clean_word'], 
                'answer_str': "".join(pw['clean_word']),
                'clue': pw['original_data']['clue'],
                'start_x': pw['x'] - min_x,
                'start_y': pw['y'] - min_y,
                'direction': pw['direction'],
                'number': 0 
            })
        final_words.sort(key=lambda w: (w['start_y'], w['start_x']))
        current_num = 1
        start_coords = {}
        for w in final_words:
            coord = (w['start_x'], w['start_y'])
            if coord not in start_coords:
                start_coords[coord] = current_num
                current_num += 1
            w['number'] = start_coords[coord]
        return {
            'width': width,
            'height': height,
            'words': final_words,
            'placed_count': len(final_words),
            'total_count': total_input_count
        }
