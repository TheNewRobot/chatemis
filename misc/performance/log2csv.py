import re
import csv
from datetime import datetime

# sudo tegrastats --interval 1000 > jetson_stats.log

def log_to_csv(input_file, output_file):
    """
    Convert Jetson stats log file to CSV format
    
    Args:
        input_file (str): Path to the input .log file
        output_file (str): Path to the output .csv file
    """
    # Define the header based on the log file structure
    header = [
        'timestamp', 'date', 'time',
        'RAM_used', 'RAM_total', 'RAM_unit',
        'lfb', 'SWAP_used', 'SWAP_total', 'SWAP_unit', 'cached',
        'CPU1_load', 'CPU1_freq', 'CPU2_load', 'CPU2_freq', 'CPU3_load', 'CPU3_freq',
        'CPU4_load', 'CPU4_freq', 'CPU5_load', 'CPU5_freq', 'CPU6_load', 'CPU6_freq',
        'GR3D_FREQ',
        'cpu_temp', 'soc2_temp', 'soc0_temp', 'gpu_temp', 'tj_temp', 'soc1_temp',
        'VDD_IN_current', 'VDD_IN_average', 'VDD_CPU_GPU_CV_current', 'VDD_CPU_GPU_CV_average',
        'VDD_SOC_current', 'VDD_SOC_average'
    ]
    
    with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        
        for line in f_in:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Parse timestamp, date and time
            timestamp_match = re.match(r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                date, time = timestamp.split(' ')
                
                # Extract RAM information
                ram_match = re.search(r'RAM (\d+)/(\d+)(\w+) \(lfb (.+?)\)', line)
                ram_used = ram_match.group(1) if ram_match else ''
                ram_total = ram_match.group(2) if ram_match else ''
                ram_unit = ram_match.group(3) if ram_match else ''
                lfb = ram_match.group(4) if ram_match else ''
                
                # Extract SWAP information
                swap_match = re.search(r'SWAP (\d+)/(\d+)(\w+) \(cached (.+?)\)', line)
                swap_used = swap_match.group(1) if swap_match else ''
                swap_total = swap_match.group(2) if swap_match else ''
                swap_unit = swap_match.group(3) if swap_match else ''
                cached = swap_match.group(4) if swap_match else ''
                
                # Extract CPU information
                cpu_match = re.search(r'CPU \[(.*?)\]', line)
                cpu_info = []
                if cpu_match:
                    cpu_entries = cpu_match.group(1).split(',')
                    for entry in cpu_entries:
                        load_freq = re.search(r'(\d+)%@(\d+)', entry.strip())
                        if load_freq:
                            cpu_info.append(load_freq.group(1))
                            cpu_info.append(load_freq.group(2))
                
                # Pad CPU info to ensure 12 elements (6 CPUs with load and freq)
                cpu_info.extend([''] * (12 - len(cpu_info)))
                
                # Extract GR3D_FREQ
                gr3d_match = re.search(r'GR3D_FREQ (\d+)%', line)
                gr3d_freq = gr3d_match.group(1) if gr3d_match else ''
                
                # Extract temperature information
                temp_pattern = r'(\w+)@([\d.]+)C'
                temperatures = {}
                for temp_match in re.finditer(temp_pattern, line):
                    temperatures[temp_match.group(1)] = temp_match.group(2)
                
                cpu_temp = temperatures.get('cpu', '')
                soc2_temp = temperatures.get('soc2', '')
                soc0_temp = temperatures.get('soc0', '')
                gpu_temp = temperatures.get('gpu', '')
                tj_temp = temperatures.get('tj', '')
                soc1_temp = temperatures.get('soc1', '')
                
                # Extract power information
                power_pattern = r'(\w+) (\d+)mW/(\d+)mW'
                power_info = {}
                for power_match in re.finditer(power_pattern, line):
                    power_info[power_match.group(1)] = (power_match.group(2), power_match.group(3))
                
                vdd_in = power_info.get('VDD_IN', ('', ''))
                vdd_cpu_gpu_cv = power_info.get('VDD_CPU_GPU_CV', ('', ''))
                vdd_soc = power_info.get('VDD_SOC', ('', ''))
                
                # Create row with all parsed information
                row = [
                    timestamp, date, time,
                    ram_used, ram_total, ram_unit,
                    lfb, swap_used, swap_total, swap_unit, cached,
                    *cpu_info,
                    gr3d_freq,
                    cpu_temp, soc2_temp, soc0_temp, gpu_temp, tj_temp, soc1_temp,
                    vdd_in[0], vdd_in[1], vdd_cpu_gpu_cv[0], vdd_cpu_gpu_cv[1], vdd_soc[0], vdd_soc[1]
                ]
                
                writer.writerow(row)
    
    print(f"Conversion complete. Output saved to {output_file}")

if __name__ == "__main__":
    # Define input and output file paths directly within the script
    input_file = "jetson_stats.log"
    output_file = "jetson_stats.csv"
    
    # Call the conversion function
    log_to_csv(input_file, output_file)