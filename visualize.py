import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io
import base64

def plot_metrics(metrics, title_prefix, method, json_type):
    plt.figure(figsize=(7, 5))
    print(method)
    if method != 'Python Libraries':
        x_data = range(0, len(metrics['results_times']))
        plt.plot(x_data, metrics['results_times'], linestyle='-', color='grey')
        
        valid_indices = [idx + 1 for idx, valid in enumerate(metrics.get('result_validity', [])) if valid]
        invalid_indices = [idx + 1 for idx, valid in enumerate(metrics.get('result_validity', [])) if not valid]

        if valid_indices:
            plt.scatter(valid_indices, [metrics['results_times'][idx] for idx in valid_indices], marker='o', s=50, color='g', label='Valid Result')
        if invalid_indices:
            plt.scatter(invalid_indices, [metrics['results_times'][idx] for idx in invalid_indices], marker='o', s=50, color='r', label='Invalid Result')
        
        if metrics['result_validity'].count(True) > 1:
            plt.axhline(y=metrics['avg_time_per_record'], color='m', linestyle='--', label=f'Avg Time per (valid) Result ({metrics["avg_time_per_record"]:.2f} s)')

    plt.axhline(y=metrics['generation_time'], color='m', linestyle='-', label=f'Generation Time ({metrics["generation_time"]:.4f} s)')
    
    if method == 'Python Libraries' and len(metrics['results_times']) > 2:
        plt.axhline(y=metrics['avg_time_per_record'], color='m', linestyle='--', label=f'Avg Time per (valid) Result ({metrics["avg_time_per_record"]:.4f} s)')

    max_y = max(max(metrics.get('results_times', [0])), metrics.get('generation_time', 0), metrics.get('avg_time_per_record', 0))
    plt.ylim(0, max_y * 1.1)
    
    plt.xticks(range(1, len(metrics['results_times'])))
    plt.xlabel('Entry')
    plt.ylabel('Time (s)')
    plt.title(f'{title_prefix} for {json_type} with {method}')
    plt.legend()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_base64 = base64.b64encode(img.getvalue()).decode()
    
    plt.clf()
    
    return plot_base64

def visualize_data(time_metrics, saved_json_data, cur_method, json_type):
    plot_base64_list = []
    visualization_html = ""

    # Plot current results if available
    if time_metrics:
        plot_base64 = plot_metrics(time_metrics, 'Results', cur_method, json_type)
        plot_base64_list.append(plot_base64)

    # Plot saved results if available
    if saved_json_data:
        plot_base64_saved = plot_metrics(saved_json_data, 'Saved Results', saved_json_data['generation_method'], saved_json_data['json_type'])
        plot_base64_list.append(plot_base64_saved)

    # Construct the HTML to display the plot images
    for idx, plot_base64 in enumerate(plot_base64_list):
        visualization_html += f'<img src="data:image/png;base64,{plot_base64}" alt="Performance Metrics {idx+1}">'
    
    return visualization_html
