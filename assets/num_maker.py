import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from decimal import Decimal
import re

# ---------------------------------------------------------------------------
# REVERSE ENGINE CORE (PRECISION UPGRADED)
# ---------------------------------------------------------------------------

def reverse_num_conv(mode, data):
    """
    Takes structural UI data and packs it into the 10-byte hex format.
    area1: 1 hex digit
    area2: 15 hex digits
    area3: 2 hex digits
    area4: 2 hex digits
    Total = 20 hex digits (10 bytes)
    """
    try:
        if mode == "Float":
            val_str = data['value'].strip().lower()
            
            # Treat 0 or empty inputs as an absolute zero block
            if not val_str or Decimal(val_str) == Decimal('0'):
                return "00" * 10
                
            # Parse using Decimal to avoid standard float precision loss!
            dec_val = Decimal(val_str)
            sign = "-" if dec_val < 0 else "+"
            dec_abs = abs(dec_val)
            
            # Extract engineering/scientific notation parts cleanly via strings
            # This extracts scientific parts without falling back to float truncation
            s_num = f"{dec_abs:e}" 
            if 'e' in s_num:
                mantissa, exp_str = s_num.split('e')
                exp = int(exp_str)
            else:
                mantissa = s_num
                exp = 0
                
            # Clean up the mantissa digits to fill area2
            digits = mantissa.replace('.', '')
            area2 = digits.ljust(15, '0')[:15]
                
            area1 = "0"
            if sign == "+":
                area4 = 1 if exp >= 0 else 0
            else:
                area4 = 6 if exp >= 0 else 5
                
            if exp >= 0:
                area3 = exp
            else:
                area3 = 100 - abs(exp)
                
            return f"{area1}{area2}{area3:02d}{area4:02d}"

        elif mode == "Fraction":
            sign = data['sign']
            whole = data['whole'].strip()
            num = data['num'].strip()
            den = data['den'].strip()
            
            if not num or not den:
                raise ValueError("Numerator and Denominator fields are required.")
                
            if whole:
                area2_str = f"{whole}a{num}a{den}"
            else:
                area2_str = f"{num}a{den}"
                
            area3 = len(area2_str)
            area2_padded = area2_str.ljust(15, '0')[:15]
            
            area1 = "2"
            area4 = "01" if sign == "-" else "06"
            
            return f"{area1}{area2_padded}{area3:02d}{area4}"

        elif mode == "Radical":
            a4 = "01" if data['sign1'] == "-" else "06"
            a3 = "01" if data['sign2'] == "-" else "06"
            
            rad1 = f"{int(data['rad1']):03d}"
            num1 = f"{int(data['num1']):02d}"
            den1 = f"{int(data['den1']):02d}"
            
            rad2 = f"{int(data['rad2']):03d}"
            num2 = f"{int(data['num2']):02d}"
            den2 = f"{int(data['den2']):02d}"
            
            area1 = "8"
            area2 = f"{rad1}{num1}{den1}0{rad2}{num2}{den2}"
            
            return f"{area1}{area2}{a3}{a4}"

        elif mode == "Error":
            error_mapping = {
                'AC Break': 1, 'Syntax ERROR': 2, 'Math ERROR': 3, 
                'Insufficient MEM': 4, 'Stack ERROR': 7, 'Argument ERROR': 8, 
                'Dimension ERROR': 9, "Can't Solve": 10, 'Time Out': 11, 
                'Variable ERROR': 12, 'NULL ERROR': 13
            }
            err_code = error_mapping.get(data['err_type'], 0)
            area1 = "f"
            area2 = f"{err_code:x}".ljust(15, '0')[:15]
            return f"{area1}{area2}0000"

    except Exception as e:
        raise ValueError(f"Encoding operation failed. Details: {e}")

# ---------------------------------------------------------------------------
# PROFESSIONAL UI INTERFACE
# ---------------------------------------------------------------------------

class CorporateByteEncoder:
    def __init__(self, root):
        self.root = root
        self.root.title("10-Byte Hex Encoder and Translation Tool")
        self.root.geometry("700x520")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Professional Heading
        title_label = ttk.Label(root, text="10-BYTE HEXADECIMAL CODER", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=15)
        
        # Notebook Structure
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Mode Tabs
        self.tab_float = ttk.Frame(self.notebook, padding=15)
        self.tab_frac = ttk.Frame(self.notebook, padding=15)
        self.tab_rad = ttk.Frame(self.notebook, padding=15)
        self.tab_err = ttk.Frame(self.notebook, padding=15)
        
        self.notebook.add(self.tab_float, text=" Floating Point / Zero ")
        self.notebook.add(self.tab_frac, text=" Fractional Format ")
        self.notebook.add(self.tab_rad, text=" Radical Format ")
        self.notebook.add(self.tab_err, text=" Exception Error ")
        
        self.setup_float_tab()
        self.setup_frac_tab()
        self.setup_rad_tab()
        self.setup_err_tab()
        
        # Process Execution Trigger
        self.gen_btn = ttk.Button(root, text="Generate Data Stream", command=self.process_current_tab)
        self.gen_btn.pack(pady=15)
        
        # Output Interface Section
        out_frame = ttk.LabelFrame(root, text=" Output Registration Registers ", padding=15)
        out_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(out_frame, text="Hexadecimal Output:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.hex_out = ttk.Entry(out_frame, font=("Consolas", 12), width=45)
        self.hex_out.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=4)
        
        ttk.Label(out_frame, text="Byte Representation:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.bytes_out = ttk.Entry(out_frame, font=("Consolas", 11), width=45)
        self.bytes_out.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=4)
        
        out_frame.columnconfigure(1, weight=1)

    # --- INPUT LAYER INITIALIZATIONS ---
    def setup_float_tab(self):
        ttk.Label(self.tab_float, text="Value Input Field (Supports Standard Decimals, Exponents, and 0):", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        self.float_var = tk.StringVar(value="1.23456789112345e67")
        entry = ttk.Entry(self.tab_float, textvariable=self.float_var, font=("Consolas", 11), width=45)
        entry.pack(fill=tk.X, pady=5)

    def setup_frac_tab(self):
        ttk.Label(self.tab_frac, text="Fraction Component Assembly Range:", font=("Helvetica", 11, "bold")).grid(row=0, column=0, columnspan=5, sticky=tk.W, pady=10)
        
        self.frac_sign = ttk.Combobox(self.tab_frac, values=["+", "-"], width=4, state="readonly")
        self.frac_sign.set("+")
        self.frac_sign.grid(row=1, column=0, padx=5)
        
        self.frac_whole = ttk.Entry(self.tab_frac, font=("Consolas", 11), width=8, justify="center")
        self.frac_whole.grid(row=1, column=1, padx=5)
        ttk.Label(self.tab_frac, text="Whole (Optional)", font=("Helvetica", 9, "italic")).grid(row=2, column=1)
        
        self.frac_num = ttk.Entry(self.tab_frac, font=("Consolas", 11), width=8, justify="center")
        self.frac_num.grid(row=1, column=2, padx=5)
        ttk.Label(self.tab_frac, text="Numerator", font=("Helvetica", 9)).grid(row=2, column=2)
        
        ttk.Label(self.tab_frac, text="/", font=("Helvetica", 14, "bold")).grid(row=1, column=3, padx=2)
        
        self.frac_den = ttk.Entry(self.tab_frac, font=("Consolas", 11), width=8, justify="center")
        self.frac_den.grid(row=1, column=4, padx=5)
        ttk.Label(self.tab_frac, text="Denominator", font=("Helvetica", 9)).grid(row=2, column=4)

    def setup_rad_tab(self):
        ttk.Label(self.tab_rad, text="Radical Base Configuration Layout:", font=("Helvetica", 11, "bold")).grid(row=0, column=0, columnspan=7, sticky=tk.W, pady=10)
        
        # --- Component A ---
        ttk.Label(self.tab_rad, text="Primary Segment Expression:", font=("Helvetica", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.rad1_sign = ttk.Combobox(self.tab_rad, values=["+", "-"], width=3, state="readonly")
        self.rad1_sign.set("+")
        self.rad1_sign.grid(row=2, column=0, padx=2)
        
        ttk.Label(self.tab_rad, text="√").grid(row=2, column=1)
        self.rad1_val = ttk.Entry(self.tab_rad, font=("Consolas", 11), width=5, justify="center")
        self.rad1_val.insert(0, "2")
        self.rad1_val.grid(row=2, column=2, padx=2)
        
        ttk.Label(self.tab_rad, text=" * (").grid(row=2, column=3)
        self.rad1_num = ttk.Entry(self.tab_rad, font=("Consolas", 11), width=4, justify="center")
        self.rad1_num.insert(0, "1")
        self.rad1_num.grid(row=2, column=4, padx=2)
        ttk.Label(self.tab_rad, text="/").grid(row=2, column=5)
        self.rad1_den = ttk.Entry(self.tab_rad, font=("Consolas", 11), width=4, justify="center")
        self.rad1_den.insert(0, "1")
        self.rad1_den.grid(row=2, column=6, padx=2)
        ttk.Label(self.tab_rad, text=")").grid(row=2, column=7)
        
        # Vertical Separation Margin
        ttk.Label(self.tab_rad, text="").grid(row=3, column=0, pady=4)
        
        # --- Component B ---
        ttk.Label(self.tab_rad, text="Secondary Segment Expression:", font=("Helvetica", 9, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rad2_sign = ttk.Combobox(self.tab_rad, values=["+", "-"], width=3, state="readonly")
        self.rad2_sign.set("+")
        self.rad2_sign.grid(row=5, column=0, padx=2)
        
        ttk.Label(self.tab_rad, text="√").grid(row=5, column=1)
        self.rad2_val = ttk.Entry(self.tab_rad, font=("Consolas", 11), width=5, justify="center")
        self.rad2_val.insert(0, "3")
        self.rad2_val.grid(row=5, column=2, padx=2)
        
        ttk.Label(self.tab_rad, text=" * (").grid(row=5, column=3)
        self.rad2_num = ttk.Entry(self.tab_rad, font=("Consolas", 11), width=4, justify="center")
        self.rad2_num.insert(0, "1")
        self.rad2_num.grid(row=5, column=4, padx=2)
        ttk.Label(self.tab_rad, text="/").grid(row=5, column=5)
        self.rad2_den = ttk.Entry(self.tab_rad, font=("Consolas", 11), width=4, justify="center")
        self.rad2_den.insert(0, "1")
        self.rad2_den.grid(row=5, column=6, padx=2)
        ttk.Label(self.tab_rad, text=")").grid(row=5, column=7)

    def setup_err_tab(self):
        ttk.Label(self.tab_err, text="Target Exception System Code:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        self.err_combo = ttk.Combobox(self.tab_err, state="readonly", width=30,
                                      values=['AC Break', 'Syntax ERROR', 'Math ERROR', 'Insufficient MEM', 
                                              'Stack ERROR', 'Argument ERROR', 'Dimension ERROR', 
                                              "Can't Solve", 'Time Out', 'Variable ERROR', 'NULL ERROR'])
        self.err_combo.set('Math ERROR')
        self.err_combo.pack(fill=tk.X, pady=5)

    # --- RUNTIME OPERATIONS DISPATCHER ---
    def process_current_tab(self):
        index = self.notebook.index(self.notebook.select())
        mode_map = {0: "Float", 1: "Fraction", 2: "Radical", 3: "Error"}
        mode = mode_map[index]
        
        payload = {}
        
        if mode == "Float":
            payload['value'] = self.float_var.get()
        elif mode == "Fraction":
            payload['sign'] = self.frac_sign.get()
            payload['whole'] = self.frac_whole.get()
            payload['num'] = self.frac_num.get()
            payload['den'] = self.frac_den.get()
        elif mode == "Radical":
            payload['sign1'] = self.rad1_sign.get()
            payload['rad1'] = self.rad1_val.get()
            payload['num1'] = self.rad1_num.get()
            payload['den1'] = self.rad1_den.get()
            
            payload['sign2'] = self.rad2_sign.get()
            payload['rad2'] = self.rad2_val.get()
            payload['num2'] = self.rad2_num.get()
            payload['den2'] = self.rad2_den.get()
        elif mode == "Error":
            payload['err_type'] = self.err_combo.get()
            
        try:
            generated_hex = reverse_num_conv(mode, payload)
            
            if len(generated_hex) != 20:
                raise ValueError(f"Stream verification mismatch. Expected length 20, compiled {len(generated_hex)}.")
                
            self.hex_out.delete(0, tk.END)
            self.hex_out.insert(0, generated_hex)
            
            bytes_repr = "b'" + "".join(f"\\x{generated_hex[i:i+2]}" for i in range(0, len(generated_hex), 2)) + "'"
            self.bytes_out.delete(0, tk.END)
            self.bytes_out.insert(0, bytes_repr)
            
        except Exception as err:
            messagebox.showerror("Execution Fault", str(err))

if __name__ == "__main__":
    window = tk.Tk()
    app = CorporateByteEncoder(window)
    window.mainloop()
