import os
import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for frontend applications to communicate with this API
CORS(app)

@app.route('/calculate', methods=['POST'])
def calculate_bag_production():
    try:
        data = request.get_json() or {}
        
        # 1. Map inputs safely with fallback defaults
        bag_width = float(data.get("bag_width", 0))
        bag_height = float(data.get("bag_height", 0))
        num_bags = int(data.get("num_bags", 0))
        panna = float(data.get("panna", 0))
        
        top_allowance = float(data.get("top_allowance", 0))
        side_allowance = float(data.get("side_allowance", 0))
        bottom_allowance = 0.5  # Fixed common bottom allowance
        
        # Handle Inputs 
        handle_length = float(data.get("handle_length", 0))
        handle_width = float(data.get("handle_width", 0))
        handles_per_bag = int(data.get("handles_per_bag", 0))
        
        cost_per_meter = float(data.get("cost_per_meter", 0))
        
        total_handles_needed = num_bags * handles_per_bag

        def evaluate_style(style_name, cut_w, cut_h):
            # Safe boundary check
            if cut_w <= 0 or cut_h <= 0 or panna <= 0 or num_bags <= 0:
                return {
                    "style_name": style_name, "cut_w": float(cut_w), "cut_h": float(cut_h),
                    "best_layout": "Invalid inputs", "bags_per_row": 0, "leftover_width": 0.0,
                    "handles_from_scrap": 0, "extra_handles_needed": 0, "bag_meters": 0.0,
                    "extra_handle_meters": 0.0, "total_meters": 0.0, "total_cost": 0.0
                }

            # --- Option 1: All Straight (Width along Panna) ---
            fit_1 = panna // cut_w
            if fit_1 > 0:
                rows_1 = math.ceil(num_bags / fit_1)
                len_1 = rows_1 * cut_h
            else:
                len_1, fit_1 = float('inf'), 0

            # --- Option 2: All Rotated (Height along Panna) ---
            fit_2 = panna // cut_h
            if fit_2 > 0:
                rows_2 = math.ceil(num_bags / fit_2)
                len_2 = rows_2 * cut_w
            else:
                len_2, fit_2 = float('inf'), 0

            # --- Option 3: Mixed Combo Layout ---
            len_combo = float('inf')
            straight_rows = 0
            rotated_rows = 0
            
            if fit_1 > 0 and fit_2 > 0 and num_bags > fit_1:
                straight_rows = num_bags // fit_1
                bags_left = num_bags - (straight_rows * fit_1)
                
                if bags_left > 0:
                    rotated_rows = math.ceil(bags_left / fit_2)
                    possible_combo_len = (straight_rows * cut_h) + (rotated_rows * cut_w)
                    
                    if possible_combo_len < len_1 and possible_combo_len < len_2:
                        len_combo = possible_combo_len

            # Decide layout orientation
            if len_combo <= len_1 and len_combo <= len_2:
                layout_desc = f"Mixed Combo ({straight_rows} rows straight + {rotated_rows} rows rotated)"
                bag_inches = len_combo
                
                len_sec_a = straight_rows * cut_h
                rem_w_a = panna % cut_w
                handles_w_a = rem_w_a // handle_width if handle_width > 0 else 0
                handles_l_a = len_sec_a // handle_length if handle_length > 0 else 0
                handles_from_a = handles_w_a * handles_l_a
                
                len_sec_b = rotated_rows * cut_w
                rem_w_b = panna % cut_h
                handles_w_b = rem_w_b // handle_width if handle_width > 0 else 0
                handles_l_b = len_sec_b // handle_length if handle_length > 0 else 0
                handles_from_b = handles_w_b * handles_l_b
                
                total_handles_from_scrap = handles_from_a + handles_from_b
                leftover_width_display = rem_w_a
                bags_per_row_display = fit_1
                
            elif len_1 <= len_2:
                layout_desc = "All Width along Panna"
                bag_inches = len_1
                rem_w_1 = panna % cut_w
                handles_w_1 = rem_w_1 // handle_width if handle_width > 0 else 0
                handles_l_1 = len_1 // handle_length if handle_length > 0 else 0
                total_handles_from_scrap = handles_w_1 * handles_l_1
                leftover_width_display = rem_w_1
                bags_per_row_display = fit_1
            else:
                layout_desc = "All Height along Panna (Rotated)"
                bag_inches = len_2
                rem_w_2 = panna % cut_h
                handles_w_2 = rem_w_2 // handle_width if handle_width > 0 else 0
                # FIXED: Changed from handle_width to handle_length
                handles_l_2 = len_2 // handle_length if handle_length > 0 else 0 
                total_handles_from_scrap = handles_w_2 * handles_l_2
                leftover_width_display = rem_w_2
                bags_per_row_display = fit_2

            # Safe zero checks for handles
            if total_handles_needed == 0 or handle_width == 0 or handle_length == 0:
                total_handles_from_scrap = 0
                remaining_handles_to_cut = 0
                extra_handle_inches = 0
            else:
                if total_handles_from_scrap > total_handles_needed:
                    total_handles_from_scrap = total_handles_needed
                remaining_handles_to_cut = total_handles_needed - total_handles_from_scrap
                
                handles_per_panna_row = panna // handle_width
                if handles_per_panna_row > 0:
                    extra_handle_rows = math.ceil(remaining_handles_to_cut / handles_per_panna_row)
                    extra_handle_inches = extra_handle_rows * handle_length
                else:
                    extra_handle_inches = 0

            final_total_inches = bag_inches + extra_handle_inches
            total_meters = (final_total_inches * 2.54) / 100.0
            total_cost = total_meters * cost_per_meter

            return {
                "style_name": style_name,
                "cut_w": float(cut_w),
                "cut_h": float(cut_h),
                "best_layout": layout_desc,
                "bags_per_row": int(bags_per_row_display),
                "leftover_width": float(leftover_width_display),
                "handles_from_scrap": int(total_handles_from_scrap),
                "extra_handles_needed": int(remaining_handles_to_cut),
                "bag_meters": float((bag_inches * 2.54) / 100.0),
                "extra_handle_meters": float((extra_handle_inches * 2.54) / 100.0),
                "total_meters": float(total_meters),
                "total_cost": float(total_cost)
            }

        # Process styles
        box_w = (2 * bag_width) + side_allowance
        box_h = bag_height + bottom_allowance + top_allowance
        box_result = evaluate_style("Box Cutting", box_w, box_h)

        u_w = bag_width + side_allowance
        u_h = (2 * bag_height) + (2 * top_allowance)
        u_result = evaluate_style("U Cutting", u_w, u_h)

        best_style = box_result if box_result["total_meters"] <= u_result["total_meters"] else u_result

        return jsonify({
            "status": "success",
            "total_handles_needed": total_handles_needed,
            "box_analysis": box_result,
            "u_analysis": u_result,
            "recommendation": {
                "best_style": best_style["style_name"],
                "total_meters": best_style["total_meters"],
                "total_cost": best_style["total_cost"],
                # FIXED: Protect against division by zero error
                "average_cost_per_bag": best_style["total_cost"] / num_bags if num_bags > 0 else 0
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    # FIXED: Use Render's environment port variable with local fallback 
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
