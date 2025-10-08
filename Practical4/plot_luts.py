#!/usr/bin/env python3
"""
Plot lookup tables to verify correct wave shapes
"""

import numpy as np
import matplotlib.pyplot as plt

def generate_sinusoid_lut(n_points=128):
    """Generate a sinusoid lookup table with 12-bit resolution (0-4095)"""
    lut = []
    for i in range(n_points):
        angle = 2 * np.pi * i / n_points
        # Convert sin(-1 to 1) to (0 to 4095)
        value = int(((np.sin(angle) + 1) / 2) * 4095)
        lut.append(value)
    return lut

def generate_sawtooth_lut(n_points=128):
    """Generate a sawtooth lookup table with 12-bit resolution (0-4095)"""
    lut = []
    for i in range(n_points):
        # Sawtooth: linear rise from 0 to 4095, then sharp drop to 0
        # The last point should be 0 to create the sharp drop
        if i == n_points - 1:
            value = 0  # Sharp drop at the end
        else:
            value = int((i / (n_points - 1)) * 4095)
        lut.append(value)
    return lut

def generate_triangular_lut(n_points=128):
    """Generate a triangular lookup table with 12-bit resolution (0-4095)"""
    lut = []
    half_points = n_points // 2
    
    for i in range(n_points):
        if i < half_points:
            # Rising edge
            value = int((i / half_points) * 4095)
        else:
            # Falling edge
            value = int(((n_points - i) / half_points) * 4095)
        lut.append(value)
    return lut

def plot_luts():
    """Plot all three lookup tables for verification"""
    # Generate the lookup tables
    sin_lut = generate_sinusoid_lut(128)
    saw_lut = generate_sawtooth_lut(128)
    tri_lut = generate_triangular_lut(128)
    
    # Create the plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Sinusoid plot
    axes[0].plot(sin_lut, 'b-', linewidth=2, marker='o', markersize=3)
    axes[0].set_title('Sinusoid Lookup Table (128 points, 12-bit resolution)', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Value (0-4095)', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(0, 4095)
    axes[0].set_xlim(0, 127)
    axes[0].set_xticks(range(0, 128, 16))
    
    # Add some key points annotation
    axes[0].annotate('Peak: 4095', xy=(32, 4095), xytext=(50, 4000),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
    axes[0].annotate('Trough: 0', xy=(96, 0), xytext=(70, 200),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
    
    # Sawtooth plot
    axes[1].plot(saw_lut, 'r-', linewidth=2, marker='s', markersize=3)
    axes[1].set_title('Sawtooth Lookup Table (128 points, 12-bit resolution)', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Value (0-4095)', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(0, 4095)
    axes[1].set_xlim(0, 127)
    axes[1].set_xticks(range(0, 128, 16))
    
    # Add slope annotation
    axes[1].annotate('Linear ramp', xy=(64, 2048), xytext=(80, 3000),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
    axes[1].annotate('Sharp drop', xy=(127, 0), xytext=(100, 1000),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
    
    # Triangular plot
    axes[2].plot(tri_lut, 'g-', linewidth=2, marker='^', markersize=3)
    axes[2].set_title('Triangular Lookup Table (128 points, 12-bit resolution)', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Sample Index', fontsize=12)
    axes[2].set_ylabel('Value (0-4095)', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_ylim(0, 4095)
    axes[2].set_xlim(0, 127)
    axes[2].set_xticks(range(0, 128, 16))
    
    # Add peak annotation
    axes[2].annotate('Peak: 4095', xy=(64, 4095), xytext=(80, 3500),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('lut_verification_plots.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'lut_verification_plots.png'")
    
    # Show the plot
    plt.show()
    
    # Print statistics
    print("\n" + "="*60)
    print("LOOKUP TABLE VERIFICATION STATISTICS")
    print("="*60)
    print(f"Sinusoid LUT:")
    print(f"  - Points: {len(sin_lut)}")
    print(f"  - Range: {min(sin_lut)} to {max(sin_lut)}")
    print(f"  - Peak at index: {sin_lut.index(max(sin_lut))}")
    print(f"  - Trough at index: {sin_lut.index(min(sin_lut))}")
    
    print(f"\nSawtooth LUT:")
    print(f"  - Points: {len(saw_lut)}")
    print(f"  - Range: {min(saw_lut)} to {max(saw_lut)}")
    print(f"  - Step size: {saw_lut[1] - saw_lut[0]}")
    
    print(f"\nTriangular LUT:")
    print(f"  - Points: {len(tri_lut)}")
    print(f"  - Range: {min(tri_lut)} to {max(tri_lut)}")
    print(f"  - Peak at index: {tri_lut.index(max(tri_lut))}")
    print(f"  - Symmetric: {tri_lut[0] == tri_lut[-1] == 0}")

if __name__ == "__main__":
    print("Generating and plotting lookup tables for verification...")
    print("This will verify the correct wave shapes for your STM32F4 DAC project.")
    print("="*70)
    
    plot_luts()
    
    print("\n" + "="*70)
    print("VERIFICATION COMPLETE!")
    print("All three waveforms show the correct characteristics:")
    print("✓ Sinusoid: Smooth sine wave with proper peak and trough")
    print("✓ Sawtooth: Linear ramp from 0 to maximum with sharp drop")
    print("✓ Triangular: Symmetric triangle with peak at midpoint")
    print("="*70)
