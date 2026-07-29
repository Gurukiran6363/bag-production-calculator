# Bag Production Fabric & Cost Calculator

An industrial-grade, object-oriented production layout calculator designed for textile workshops and bag manufacturing units. It automatically evaluates and compares cutting styles side-by-side to minimize fabric roll (Panna) wastage and maximizes handle salvage from layout scrap.

## 📁 Project Structure
- `frontend/index.html` - Class-based interactive web dashboard for real-time workshop estimation.
- `backend/bag1.py` - Object-oriented Python engine for terminal-based layout calculations.

## 🛠️ Layout Features Supported
1. **Box Cutting Layout** (Side-folded panel math with single top/bottom allowances).
2. **U Cutting Layout** (Bottom-folded panel math with doubled top allowances).
3. **Mixed Combo Orientation** (Optimizes a single run by packing straight rows and rotating remaining pieces to completely eliminate trailing end waste).
4. **Scrap-Utilization Handle Engine** (Calculates salvageable strips matching custom handle dimensions before buying deficit fabric).

## 🚀 How to Run The Project
- **Web User Interface:** Go into the `frontend` folder and double-click `index.html` to open it instantly in any web browser (Chrome, Edge, Safari).
- **Python Terminal Engine:** Open your PowerShell/Terminal, navigate to the `backend` folder, and execute:
  ```powershell
  python bag1.py
  ```
