import math

def calculate_bag_production():
    print("=" * 65)
    print("  BAG FABRIC, HANDLE & COST CALCULATOR (ACCURATE COMBO VERSION)")
    print("=" * 65)
    
    # 1. User Inputs
    bag_width = float(input("Enter Bag Width (inches): "))
    bag_height = float(input("Enter Bag Height (inches): "))
    num_bags = int(input("Enter Number of Bags to make: "))
    panna = float(input("Enter Fabric Roll Width / Panna (inches): "))
    
    top_allowance = float(input("Enter TOP stitching allowance per edge (inches): "))
    side_allowance = float(input("Enter TOTAL SIDE stitching allowance (inches): "))
    bottom_allowance = 0.5  # Fixed common bottom allowance
    
    # Handle Inputs 
    handle_length = float(input("Enter SINGLE Handle Cutting Length (inches): "))
    handle_width = float(input("Enter SINGLE Handle Cutting Width (inches): "))
    handles_per_bag = int(input("Enter Number of Handles per Bag (Usually 2): "))
    
    cost_per_meter = float(input("Enter Cost of Fabric per Meter (₹): "))
    
    total_handles_needed = num_bags * handles_per_bag

    def evaluate_style(style_name, cut_w, cut_h):
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

        # Decide which master layout takes the least fabric length
        if len_combo <= len_1 and len_combo <= len_2:
            layout_desc = f"Mixed Combo ({straight_rows} rows straight + {rotated_rows} rows rotated)"
            bag_inches = len_combo
            
            # ACCURATE HANDLE MATH: Calculate scrap from both sections independently
            # Section A (Straight Rows)
            len_sec_a = straight_rows * cut_h
            rem_w_a = panna % cut_w
            handles_w_a = rem_w_a // handle_width
            handles_l_a = len_sec_a // handle_length
            handles_from_a = handles_w_a * handles_l_a
            
            # Section B (Rotated Rows)
            len_sec_b = rotated_rows * cut_w
            rem_w_b = panna % cut_h
            handles_w_b = rem_w_b // handle_width
            handles_l_b = len_sec_b // handle_length
            handles_from_b = handles_w_b * handles_l_b
            
            total_handles_from_scrap = handles_from_a + handles_from_b
            leftover_width_display = rem_w_a  # Show dominant base row scrap width
            bags_per_row_display = fit_1
            
        elif len_1 <= len_2:
            layout_desc = "All Width along Panna"
            bag_inches = len_1
            rem_w_1 = panna % cut_w
            total_handles_from_scrap = (rem_w_1 // handle_width) * (len_1 // handle_length)
            leftover_width_display = rem_w_1
            bags_per_row_display = fit_1
        else:
            layout_desc = "All Height along Panna (Rotated)"
            bag_inches = len_2
            rem_w_2 = panna % cut_h
            total_handles_from_scrap = (rem_w_2 // handle_width) * (len_2 // handle_width) # Old logic uses width multiplier mapping
            leftover_width_display = rem_w_2
            bags_per_row_display = fit_2

        # Cap handle scrap yield
        if total_handles_from_scrap > total_handles_needed:
            total_handles_from_scrap = total_handles_needed

        remaining_handles_to_cut = total_handles_needed - total_handles_from_scrap
        
        if remaining_handles_to_cut <= 0:
            extra_handle_inches = 0
            remaining_handles_to_cut = 0
        else:
            handles_per_panna_row = panna // handle_width
            extra_handle_rows = math.ceil(remaining_handles_to_cut / handles_per_panna_row)
            extra_handle_inches = extra_handle_rows * handle_length

        final_total_inches = bag_inches + extra_handle_inches
        total_meters = (final_total_inches * 2.54) / 100.0
        total_cost = total_meters * cost_per_meter

        return {
            "style_name": style_name,
            "cut_w": cut_w,
            "cut_h": cut_h,
            "best_layout": layout_desc,
            "bags_per_row": int(bags_per_row_display),
            "leftover_width": leftover_width_display,
            "handles_from_scrap": int(total_handles_from_scrap),
            "extra_handles_needed": int(remaining_handles_to_cut),
            "bag_meters": (bag_inches * 2.54) / 100.0,
            "extra_handle_meters": (extra_handle_inches * 2.54) / 100.0,
            "total_meters": total_meters,
            "total_cost": total_cost
        }

    # Process styles
    box_w = (2 * bag_width) + side_allowance
    box_h = bag_height + bottom_allowance + top_allowance
    box_result = evaluate_style("Box Cutting", box_w, box_h)

    u_w = bag_width + side_allowance
    u_h = (2 * bag_height) + (2 * top_allowance)
    u_result = evaluate_style("U Cutting", u_w, u_h)

    # Print Breakdown
    print("\n" + "=" * 60)
    print("                     PRODUCTION BREAKDOWN")
    print("=" * 60)
    
    valid_results = []
    for res in [box_result, u_result]:
        if res is None: continue
        valid_results.append(res)
        print(f"--- {res['style_name'].upper()} ANALYSIS ---")
        print(f"Pattern Piece Size          : {res['cut_w']:.2f}\" Wide x {res['cut_h']:.2f}\" High")
        print(f"Optimal Orientation         : {res['best_layout']}")
        print(f"Bags Cut per Width Row      : {res['bags_per_row']} bags (Base Row)")
        print(f"Scrap Width (Base Row)      : {res['leftover_width']:.2f} inches")
        print(f"Total Handles Needed        : {total_handles_needed} pcs")
        print(f"Handles Obtained from Scrap : {res['handles_from_scrap']} pcs")
        print(f"Deficit Handles to cut extra: {res['extra_handles_needed']} pcs")
        print(f"Fabric for Bags Only        : {res['bag_meters']:.2f} Meters")
        print(f"Extra Fabric for Handles    : {res['extra_handle_meters']:.2f} Meters")
        print(f"TOTAL FABRIC REQUIREMENT    : {res['total_meters']:.2f} METERS")
        print(f"Estimated Cost              : ₹{res['total_cost']:.2f}")
        print("-" * 60)

    best_style = min(valid_results, key=lambda x: x['total_meters'])

    print("\n" + "★" * 60)
    print(f" FINAL RECOMMENDATION: CHOOSE {best_style['style_name'].upper()}")
    print("★" * 60)
    print(f"➔ Total Fabric to Purchase : {best_style['total_meters']:.2f} METERS 🟩")
    print(f"➔ Total Production Budget  : ₹{best_style['total_cost']:.2f}")
    print(f"➔ Average Material Cost/Bag: ₹{best_style['total_cost'] / num_bags:.2f}")
    print("=" * 60)

if __name__ == "__main__":
    calculate_bag_production()


