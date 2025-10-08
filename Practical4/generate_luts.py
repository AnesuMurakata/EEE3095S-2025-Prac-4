import numpy as np
import matplotlib.pyplot as plt

def generate_sinusoid_lut(n_points=128):
    """Generate a sinusoid lookup table with 12-bit resolution (0-4095)"""
    # Generate one complete cycle
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    # Convert to 12-bit range (0-4095)
    # sin ranges from -1 to 1, so we shift and scale to 0-4095
    lut = ((np.sin(angles) + 1) / 2) * 4095
    return lut.astype(int)

def generate_sawtooth_lut(n_points=128):
    """Generate a sawtooth lookup table with 12-bit resolution (0-4095)"""
    # Sawtooth: linear rise from 0 to 4095, then sharp drop to 0
    lut = np.linspace(0, 4095, n_points, endpoint=False)
    # Set the last point to 0 to create the sharp drop
    lut[-1] = 0
    return lut.astype(int)

def generate_triangular_lut(n_points=128):
    """Generate a triangular lookup table with 12-bit resolution (0-4095)"""
    # Create triangular wave: goes from 0 to 4095 and back to 0
    half_points = n_points // 2
    rising = np.linspace(0, 4095, half_points, endpoint=False)
    falling = np.linspace(4095, 0, n_points - half_points, endpoint=False)
    lut = np.concatenate([rising, falling])
    return lut.astype(int)

def plot_luts(sin_lut, saw_lut, tri_lut):
    """Plot all three lookup tables for verification"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Sinusoid
    axes[0].plot(sin_lut, 'b-', linewidth=2)
    axes[0].set_title('Sinusoid Lookup Table (128 points, 12-bit resolution)')
    axes[0].set_ylabel('Value (0-4095)')
    axes[0].grid(True)
    axes[0].set_ylim(0, 4095)
    
    # Sawtooth
    axes[1].plot(saw_lut, 'r-', linewidth=2)
    axes[1].set_title('Sawtooth Lookup Table (128 points, 12-bit resolution)')
    axes[1].set_ylabel('Value (0-4095)')
    axes[1].grid(True)
    axes[1].set_ylim(0, 4095)
    
    # Triangular
    axes[2].plot(tri_lut, 'g-', linewidth=2)
    axes[2].set_title('Triangular Lookup Table (128 points, 12-bit resolution)')
    axes[2].set_xlabel('Sample Index')
    axes[2].set_ylabel('Value (0-4095)')
    axes[2].grid(True)
    axes[2].set_ylim(0, 4095)
    
    plt.tight_layout()
    plt.show()

def format_for_c_array(lut, name):
    """Format lookup table as C array"""
    c_array = f"uint16_t {name}[{len(lut)}] = {{\n"
    
    # Format with 8 values per line for readability
    for i in range(0, len(lut), 8):
        line_values = lut[i:i+8]
        formatted_line = "    " + ", ".join(f"{val:4d}" for val in line_values)
        if i + 8 < len(lut):
            formatted_line += ","
        c_array += formatted_line + "\n"
    
    c_array += "};"
    return c_array

def main():
    print("Generating Lookup Tables for STM32F4 DAC...")
    print("=" * 50)
    
    # Generate lookup tables
    print("Generating sinusoid LUT...")
    sin_lut = generate_sinusoid_lut(128)
    
    print("Generating sawtooth LUT...")
    saw_lut = generate_sawtooth_lut(128)
    
    print("Generating triangular LUT...")
    tri_lut = generate_triangular_lut(128)
    
    # Print some statistics
    print(f"\nSinusoid LUT: {len(sin_lut)} points, range: {sin_lut.min()}-{sin_lut.max()}")
    print(f"Sawtooth LUT: {len(saw_lut)} points, range: {saw_lut.min()}-{saw_lut.max()}")
    print(f"Triangular LUT: {len(tri_lut)} points, range: {tri_lut.min()}-{tri_lut.max()}")
    
    # Plot for verification
    print("\nPlotting waveforms for verification...")
    plot_luts(sin_lut, saw_lut, tri_lut)
    
    # Generate C code
    print("\nGenerating C code for main.c...")
    print("=" * 50)
    
    sin_c = format_for_c_array(sin_lut, "sinusoid_lut")
    saw_c = format_for_c_array(saw_lut, "sawtooth_lut")
    tri_c = format_for_c_array(tri_lut, "triangular_lut")
    
    print("Sinusoid LUT:")
    print(sin_c)
    print("\nSawtooth LUT:")
    print(saw_c)
    print("\nTriangular LUT:")
    print(tri_c)
    
    # Save to file
    with open("waveform_luts.c", "w") as f:
        f.write("// Generated lookup tables for STM32F4 DAC\n")
        f.write("// 12-bit resolution (0-4095), 128 points per cycle\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write(sin_c + "\n\n")
        f.write(saw_c + "\n\n")
        f.write(tri_c + "\n\n")
        f.write("// LUT size constant\n")
        f.write("#define LUT_SIZE 128\n")
    
    print(f"\nC code saved to 'waveform_luts.c'")
    print("You can copy these arrays into your main.c file.")

if __name__ == "__main__":
    main()
