import matplotlib
# Use the Agg backend for Matplotlib, which is suitable for environments where a display server is not available (e.g., web applications)
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io
import base64

def plot_metrics(metrics, title_prefix, method, json_type):
    """
    Plot the performance metrics for data generation or anonymization.

    Args:
        metrics (dict): Dictionary containing timing and validity metrics.
        title_prefix (str): Prefix for the plot title (e.g., 'Results', 'Saved Results').
        method (str): The method used for data processing ('Python Libraries' or 'Large Language Model').
        json_type (str): The type of JSON data being processed.

    Returns:
        str: Base64-encoded image of the generated plot, suitable for embedding in HTML.
    """
    plt.figure(figsize=(7, 5))  # Set the figure size
    print(method)  # Debug print to verify the method being used

    # Plot timing metrics if the method is not 'Python Libraries'
    if method != 'Python Libraries':
        x_data = range(0, len(metrics['results_times']))  # X-axis data based on the number of recorded times
        plt.plot(x_data, metrics['results_times'], linestyle='-', color='grey')  # Plot the result times as a line graph
        
        # Identify indices of valid and invalid results for plotting
        valid_indices = [idx + 1 for idx, valid in enumerate(metrics.get('result_validity', [])) if valid]
        invalid_indices = [idx + 1 for idx, valid in enumerate(metrics.get('result_validity', [])) if not valid]

        # Plot valid results as green dots
        if valid_indices:
            plt.scatter(valid_indices, [metrics['results_times'][idx] for idx in valid_indices], marker='o', s=50, color='g', label='Valid Result')
        # Plot invalid results as red dots
        if invalid_indices:
            plt.scatter(invalid_indices, [metrics['results_times'][idx] for idx in invalid_indices], marker='o', s=50, color='r', label='Invalid Result')
        
        # Plot average time per valid record if there are multiple valid results
        if metrics['result_validity'].count(True) > 1:
            plt.axhline(y=metrics['avg_time_per_record'], color='m', linestyle='--', label=f'Avg Time per (valid) Result ({metrics["avg_time_per_record"]:.2f} s)')

    # Plot the overall generation time as a solid magenta line
    plt.axhline(y=metrics['generation_time'], color='m', linestyle='-', label=f'Generation Time ({metrics["generation_time"]:.4f} s)')
    
    # If the method is 'Python Libraries' and there are multiple results, plot the average time per record
    if method == 'Python Libraries' and len(metrics['results_times']) > 2:
        plt.axhline(y=metrics['avg_time_per_record'], color='m', linestyle='--', label=f'Avg Time per (valid) Result ({metrics["avg_time_per_record"]:.4f} s)')

    # Set the Y-axis limit slightly above the maximum value to give space above the highest data point
    max_y = max(max(metrics.get('results_times', [0])), metrics.get('generation_time', 0), metrics.get('avg_time_per_record', 0))
    plt.ylim(0, max_y * 1.1)
    
    # Set X-axis ticks based on the number of results
    plt.xticks(range(1, len(metrics['results_times'])))
    plt.xlabel('Entry')  # Label for the X-axis
    plt.ylabel('Time (s)')  # Label for the Y-axis
    plt.title(f'{title_prefix} for {json_type} with {method}')  # Plot title
    plt.legend()  # Show the legend

    # Save the plot to a BytesIO object in PNG format
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # Seek to the start of the BytesIO object
    plot_base64 = base64.b64encode(img.getvalue()).decode()  # Encode the plot image as a Base64 string
    
    plt.clf()  # Clear the plot to free up memory
    
    return plot_base64  # Return the Base64-encoded plot image

def visualize_data(time_metrics, saved_json_data, cur_method, json_type):
    """
    Generate HTML to display visualizations of current and saved performance metrics.

    Args:
        time_metrics (dict): Current metrics from the data processing task.
        saved_json_data (dict): Previously saved metrics for comparison.
        cur_method (str): The current method used for data processing.
        json_type (str): The type of JSON data being processed.

    Returns:
        str: HTML containing Base64-encoded images of the performance metrics.
    """
    plot_base64_list = []
    visualization_html = ""

    # Plot the current metrics if available
    if time_metrics:
        plot_base64 = plot_metrics(time_metrics, 'Results', cur_method, json_type)
        plot_base64_list.append(plot_base64)

    # Plot the saved metrics if available for comparison
    if saved_json_data:
        plot_base64_saved = plot_metrics(saved_json_data, 'Saved Results', saved_json_data['generation_method'], saved_json_data['json_type'])
        plot_base64_list.append(plot_base64_saved)

    # Construct HTML to embed the generated plot images
    for idx, plot_base64 in enumerate(plot_base64_list):
        visualization_html += f'<img src="data:image/png;base64,{plot_base64}" alt="Performance Metrics {idx+1}">'
    
    return visualization_html  # Return the generated HTML with embedded images
