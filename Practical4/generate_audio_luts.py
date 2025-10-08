#!/usr/bin/env python3
"""
Audio LUT generator that finds the most interesting part of the audio
"""

import struct
import os
import math
import matplotlib.pyplot as plt
import numpy as np

def read_wav_file(filename):
    """Read a .wav file and return audio data"""
    try:
        with open(filename, 'rb') as f:
            # Read WAV header
            riff = f.read(4)
            if riff != b'RIFF':
                raise ValueError("Not a valid WAV file")
            
            file_size = struct.unpack('<I', f.read(4))[0]
            wave = f.read(4)
            if wave != b'WAVE':
                raise ValueError("Not a valid WAV file")
            
            # Find fmt chunk
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    raise ValueError("Could not find fmt chunk")
                
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    break
                else:
                    f.seek(chunk_size, 1)  # Skip this chunk
            
            # Read fmt chunk
            fmt_data = f.read(chunk_size)
            audio_format = struct.unpack('<H', fmt_data[0:2])[0]
            num_channels = struct.unpack('<H', fmt_data[2:4])[0]
            sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
            byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
            block_align = struct.unpack('<H', fmt_data[12:14])[0]
            bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
            
            print(f"WAV Info: {num_channels} channels, {sample_rate} Hz, {bits_per_sample} bits")
            
            # Find data chunk
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    raise ValueError("Could not find data chunk")
                
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'data':
                    break
                else:
                    f.seek(chunk_size, 1)  # Skip this chunk
            
            # Read audio data
            audio_data = f.read(chunk_size)
            
            # Convert bytes to samples
            if bits_per_sample == 16:
                # 16-bit signed integers
                samples = []
                for i in range(0, len(audio_data), 2):
                    sample = struct.unpack('<h', audio_data[i:i+2])[0]
                    samples.append(sample)
            elif bits_per_sample == 8:
                # 8-bit unsigned integers
                samples = []
                for byte in audio_data:
                    samples.append(byte - 128)  # Convert to signed
            else:
                raise ValueError(f"Unsupported bit depth: {bits_per_sample}")
            
            # Convert to mono if stereo
            if num_channels == 2:
                mono_samples = []
                for i in range(0, len(samples), 2):
                    if i+1 < len(samples):
                        mono_samples.append((samples[i] + samples[i+1]) // 2)
                samples = mono_samples
            
            duration = len(samples) / sample_rate
            return sample_rate, samples, duration
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None, None, 0

def find_interesting_segment(audio_data, segment_length=128):
    """Find the most interesting segment of audio data"""
    if len(audio_data) <= segment_length:
        return audio_data
    
    # Calculate energy in sliding windows
    window_size = segment_length
    max_energy = 0
    best_start = 0
    
    for start in range(0, len(audio_data) - window_size, window_size // 4):
        segment = audio_data[start:start + window_size]
        energy = sum(x * x for x in segment)
        
        if energy > max_energy:
            max_energy = energy
            best_start = start
    
    print(f"  Found interesting segment at position {best_start} (energy: {max_energy})")
    return audio_data[best_start:best_start + window_size]

def process_audio_to_lut(filename, n_points=128):
    """Process audio file and generate lookup table"""
    sample_rate, audio_data, duration = read_wav_file(filename)
    
    if audio_data is None:
        return None, 0, 0
    
    print(f"Processing {filename}:")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Samples: {len(audio_data)}")
    print(f"  Raw range: {min(audio_data)} to {max(audio_data)}")
    
    # Find the most interesting segment
    interesting_segment = find_interesting_segment(audio_data, n_points)
    print(f"  Selected segment range: {min(interesting_segment)} to {max(interesting_segment)}")
    
    # Find the maximum absolute value for proper normalization
    max_abs = max(abs(x) for x in interesting_segment)
    print(f"  Max absolute value in segment: {max_abs}")
    
    if max_abs == 0:
        print(f"  WARNING: Selected segment is silent")
        # Create a simple test pattern instead
        lut = [int(2047 + 1000 * math.sin(2 * math.pi * i / n_points)) for i in range(n_points)]
        lut = [max(0, min(4095, x)) for x in lut]  # Clamp to 0-4095
        print(f"  Generated test pattern: {len(lut)} points, range {min(lut)}-{max(lut)}")
        return lut, sample_rate, duration
    
    # Normalize to -1 to 1 range first
    normalized = [x / max_abs for x in interesting_segment]
    print(f"  Normalized range: {min(normalized):.3f} to {max(normalized):.3f}")
    
    # Convert to 0-1 range
    normalized = [(x + 1) / 2 for x in normalized]
    print(f"  After 0-1 conversion: {min(normalized):.3f} to {max(normalized):.3f}")
    
    # Convert to 12-bit resolution (0-4095)
    lut = [int(x * 4095) for x in normalized]
    
    print(f"  Generated LUT: {len(lut)} points, range {min(lut)}-{max(lut)}")
    print(f"  LUT variation: {len(set(lut))} unique values")
    
    return lut, sample_rate, duration

def plot_audio_luts(luts, filenames, sample_rates):
    """Plot the generated audio lookup tables using matplotlib"""
    fig, axes = plt.subplots(len(luts), 1, figsize=(12, 4*len(luts)))
    
    if len(luts) == 1:
        axes = [axes]
    
    for i, (lut, filename, sample_rate) in enumerate(zip(luts, filenames, sample_rates)):
        if lut is not None:
            axes[i].plot(lut, 'b-', linewidth=2, marker='o', markersize=3)
            name = os.path.splitext(os.path.basename(filename))[0]
            axes[i].set_title(f'Audio LUT: {name.upper()} (Sample Rate: {sample_rate} Hz)', 
                            fontsize=14, fontweight='bold')
            axes[i].set_ylabel('Value (0-4095)', fontsize=12)
            axes[i].grid(True, alpha=0.3)
            axes[i].set_ylim(0, 4095)
            axes[i].set_xlim(0, len(lut)-1)
            
            # Add statistics
            axes[i].text(0.02, 0.98, f'Points: {len(lut)}\nRange: {min(lut)}-{max(lut)}\nUnique: {len(set(lut))}', 
                        transform=axes[i].transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    axes[-1].set_xlabel('Sample Index', fontsize=12)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('audio_lut_verification.png', dpi=300, bbox_inches='tight')
    print("Matplotlib plot saved as 'audio_lut_verification.png'")
    
    # Show the plot
    plt.show()

def print_ascii_plot(lut, title, width=80, height=20):
    """Create a simple ASCII plot of the audio LUT"""
    print(f"\n{title}")
    print("=" * len(title))
    
    min_val = min(lut)
    max_val = max(lut)
    range_val = max_val - min_val
    
    if range_val == 0:
        print("Flat line at", min_val)
        return
    
    # Create ASCII plot
    for row in range(height):
        y_val = max_val - (row * range_val / height)
        line = ""
        
        for i in range(width):
            x_idx = int(i * len(lut) / width)
            if x_idx >= len(lut):
                x_idx = len(lut) - 1
            
            if abs(lut[x_idx] - y_val) < (range_val / height / 2):
                line += "*"
            else:
                line += " "
        
        # Add value labels on the right
        if row == 0:
            line += f" {max_val}"
        elif row == height - 1:
            line += f" {min_val}"
        elif row == height // 2:
            line += f" {(max_val + min_val) // 2}"
        
        print(line)
    
    # Print x-axis labels
    x_labels = ""
    for i in range(0, width, 16):
        x_labels += "|" + " " * 15
    print(x_labels)
    
    # Print sample indices
    indices = ""
    for i in range(0, width, 16):
        sample_idx = int(i * len(lut) / width)
        indices += f"{sample_idx:3d}" + " " * 12
    print(indices)

def format_c_array(lut, name):
    """Format lookup table as C array"""
    c_array = f"uint32_t {name}[{len(lut)}] = {{\n"
    
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
    print("Audio LUT Generator v2 - Finds Interesting Audio Segments")
    print("=" * 60)
    
    # List of .wav files to process
    wav_files = [
        "piano.wav",
        "guitar.wav", 
        "drum.wav"
    ]
    
    # Check if files exist
    existing_files = []
    for filename in wav_files:
        if os.path.exists(filename):
            existing_files.append(filename)
            print(f"✓ Found: {filename}")
        else:
            print(f"✗ Missing: {filename}")
    
    if not existing_files:
        print("\nNo .wav files found in current directory.")
        print("Please place your .wav files in the project directory and run again.")
        return
    
    print(f"\nProcessing {len(existing_files)} audio files...")
    
    # Process each .wav file
    luts = []
    filenames = []
    sample_rates = []
    
    for filename in existing_files:
        lut, sample_rate, duration = process_audio_to_lut(filename, 128)
        luts.append(lut)
        filenames.append(filename)
        sample_rates.append(sample_rate)
        print()
    
    # Filter out failed processing
    valid_luts = [(lut, filename, sample_rate) for lut, filename, sample_rate in zip(luts, filenames, sample_rates) if lut is not None]
    
    if not valid_luts:
        print("No valid audio files processed successfully.")
        return
    
    # Generate matplotlib plots
    print("Generating matplotlib plots for verification...")
    plot_audio_luts([lut for lut, _, _ in valid_luts], 
                    [filename for _, filename, _ in valid_luts],
                    [sample_rate for _, _, sample_rate in valid_luts])
    
    # Print ASCII plots as well
    print("\nAUDIO WAVEFORM VERIFICATION (ASCII)")
    print("=" * 60)
    for lut, filename, sample_rate in valid_luts:
        name = os.path.splitext(os.path.basename(filename))[0]
        print_ascii_plot(lut, f"{name.upper()} AUDIO WAVEFORM")
    
    # Generate C code
    print("\nGenerating C code for main.c...")
    print("=" * 50)
    
    # Create C arrays for each audio file
    c_arrays = []
    for lut, filename, sample_rate in valid_luts:
        # Extract name without extension
        name = os.path.splitext(os.path.basename(filename))[0]
        c_array = format_c_array(lut, f"{name}_lut")
        c_arrays.append(c_array)
        print(f"{name.upper()} LUT:")
        print(c_array)
        print()
    
    # Save to file
    with open("audio_luts.c", "w") as f:
        f.write("// Generated audio lookup tables for STM32F4 DAC\n")
        f.write("// 12-bit resolution (0-4095), 128 points per LUT\n")
        f.write("// Generated from .wav files at 44.1kHz\n")
        f.write("// Uses most interesting audio segments\n\n")
        f.write("#include <stdint.h>\n\n")
        
        for c_array in c_arrays:
            f.write(c_array + "\n\n")
        
        f.write("// LUT size constant\n")
        f.write("#define AUDIO_LUT_SIZE 128\n")
    
    print("C code saved to 'audio_luts.c'")
    print("You can copy these arrays into your main.c file.")
    
    # Summary
    print("\n" + "=" * 60)
    print("AUDIO LUT GENERATION SUMMARY")
    print("=" * 60)
    for lut, filename, sample_rate in valid_luts:
        print(f"✓ {os.path.basename(filename)}: {len(lut)} points, range {min(lut)}-{max(lut)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
