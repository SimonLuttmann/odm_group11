"""
Central Plot Configuration for all Notebooks.

Usage in Notebooks:
    from plot_config import COLORS, setup_plot_style, get_cmap

Customization:
    Change colors in COLORS to style all plots uniformly.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib as mpl
import numpy as np

# =============================================================================
# POWERPOINT-COMPATIBLE SVG SETTINGS
# =============================================================================
# These settings prevent complex SVG constructs that PowerPoint can't render:
# - Avoids <use> and <defs> for text glyphs
# - Uses simple marker definitions

mpl.rcParams['svg.fonttype'] = 'none'      # Keep text as text, not paths
mpl.rcParams['font.family'] = 'Arial'       # Office-friendly font

# Flier (outlier) properties for boxplots - simple markers that work in PowerPoint
BOXPLOT_FLIERPROPS = {
    'marker': 'x',              # Simple 'x' marker instead of circles
    'markersize': 5,
    'markeredgecolor': 'black',
    'markeredgewidth': 1
}

# =============================================================================
# SIMULATION PARAMETERS - ADJUST HERE FOR ALL NOTEBOOKS
# =============================================================================

R_FAST = 1000      # Simulations during optimization
R_FINAL = 1500     # Simulations for final validation

# =============================================================================
# COLOR PALETTE - ADJUST HERE FOR UNIFORM DESIGN
# =============================================================================

COLORS = {
    # Primary colors for the two objectives
    'fairness': '#2E86AB',        # Blue - for Win Rate / Fairness
    'excitement': '#E94F37',      # Red/Coral - for Trick Changes / Excitement
    
    # Secondary colors for additional categories
    'secondary_1': '#F39237',     # Orange
    'secondary_2': '#7B2D8E',     # Purple
    'secondary_3': '#3DDC97',     # Green/Turquoise
    'secondary_4': '#5C5C5C',     # Gray
    
    # Algorithm colors (for comparisons)
    'nsga2': '#2E86AB',           # Blue
    'moead': '#E94F37',           # Red
    'smsemoa': '#3DDC97',         # Green
    
    # Special marker colors
    'best': '#FFD700',            # Gold - for best solutions
    'knee_point': '#9B59B6',      # Violet - for Knee Point
    'highlight': '#E74C3C',       # Red - for highlights
    
    # Pareto front colors
    'pareto_fast': '#95A5A6',     # Gray - for fast/unvalidated front
    'pareto_validated': '#2E86AB', # Blue - for validated front
    
    # Background and lines
    'grid': '#E0E0E0',            # Light gray for grid lines
    'background': '#FFFFFF',      # White
    'text': '#2C3E50',            # Dark blue/gray for text
    
    # Deck types
    'fairness_max': '#2E86AB',    # Blue
    'excitement_max': '#E94F37',  # Red
    'knee_point_deck': '#9B59B6', # Violet
    
    # Multiplayer configurations
    'config_2p': '#2E86AB',       # Blue
    'config_3p': '#E94F37',       # Red
    'config_4p': '#3DDC97',       # Green
    'config_6p': '#F39237',       # Orange
}

# Color palette as list (for iterations)
COLOR_PALETTE = [
    COLORS['fairness'],
    COLORS['excitement'],
    COLORS['secondary_1'],
    COLORS['secondary_2'],
    COLORS['secondary_3'],
    COLORS['secondary_4'],
]

# Algorithm colors as dictionary
ALGO_COLORS = {
    'NSGA-II': COLORS['nsga2'],
    'MOEA/D': COLORS['moead'],
    'SMS-EMOA': COLORS['smsemoa'],
}

# Deck type colors
DECK_COLORS = {
    'Fairness-Max': COLORS['fairness_max'],
    'Excitement-Max': COLORS['excitement_max'],
    'Knee-Point': COLORS['knee_point_deck'],
}

# =============================================================================
# ENGLISH LABELS - CENTRAL DEFINITIONS FOR ALL PLOTS
# =============================================================================

LABELS = {
    # Axis labels
    'win_rate': 'Win Rate (Fairness)',
    'trick_changes': 'Trick Changes (Excitement)',
    'hypervolume': 'Hypervolume',
    'generation': 'Generation',
    'distance': 'Distance to Best',
    'frequency': 'Frequency',
    'category': 'Category',
    'card': 'Card',
    'value': 'Value',
    
    # Legend labels
    'fast': f'Fast (R={R_FAST})',
    'validated': f'Validated (R={R_FINAL})',
    'fairness_max': 'Fairness-Max',
    'excitement_max': 'Excitement-Max',
    'knee_point': 'Knee-Point',
    'best': 'Best',
    'mean': 'Mean',
    'median': 'Median',
    
    # Titles
    'pareto_front': 'Pareto Front',
    'pareto_front_validated': 'Validated Pareto Front',
    'algorithm_comparison': 'Algorithm Comparison',
    'parameter_study': 'Parameter Study',
    'distribution': 'Distribution',
    'correlation': 'Correlation',
    'convergence': 'Convergence',
    
    # Algorithms
    'nsga2': 'NSGA-II',
    'moead': 'MOEA/D',
    'smsemoa': 'SMS-EMOA',
}

# =============================================================================
# PLOT STYLE CONFIGURATION
# =============================================================================

# Export format: 'svg' for vector graphics (scalable), 'png' for raster
EXPORT_FORMAT = 'svg'
EXPORT_DPI = 150  # Only used for PNG

PLOT_STYLE = {
    'figure.figsize': (12, 8),
    'figure.dpi': 100,
    'figure.facecolor': COLORS['background'],
    
    'axes.facecolor': COLORS['background'],
    'axes.edgecolor': COLORS['text'],
    'axes.labelcolor': COLORS['text'],
    'axes.titlesize': 26,           # Title size 26
    'axes.titleweight': 'normal',   # NOT bold
    'axes.labelsize': 20,           # Axis label size 20
    'axes.grid': True,
    'axes.axisbelow': True,
    
    'grid.color': COLORS['grid'],
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'grid.alpha': 0.7,
    
    'xtick.color': COLORS['text'],
    'ytick.color': COLORS['text'],
    'xtick.labelsize': 20,          # Tick label size 20
    'ytick.labelsize': 20,          # Tick label size 20
    
    'text.color': COLORS['text'],
    'font.size': 20,                # Base font size 20
    'font.weight': 'normal',        # NOT bold
    
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.facecolor': COLORS['background'],
    'legend.edgecolor': COLORS['grid'],
    'legend.fontsize': 16,          # Legend size 16
    
    'lines.linewidth': 2,
    'lines.markersize': 10,
    
    'scatter.marker': 'o',
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def setup_plot_style():
    """
    Applies the unified plot style to all subsequent plots.
    
    Includes PowerPoint-compatible SVG settings:
    - svg.fonttype = 'none' (text as text, not paths)
    - font.family = 'Arial' (Office-friendly)
    
    Call at the beginning of each notebook:
        from plot_config import setup_plot_style
        setup_plot_style()
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update(PLOT_STYLE)
    
    # PowerPoint-compatible SVG settings
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'Arial'
    
    print(f"✓ Plot style configured (Title=26, Labels=20, Legend=16)")
    print(f"✓ SVG mode: PowerPoint-compatible (text as text, Arial font)")
    print(f"✓ Export format: {EXPORT_FORMAT.upper()}")
    print(f"✓ R_FAST={R_FAST}, R_FINAL={R_FINAL}")


def save_plot(fig, filepath, tight=True):
    """
    Saves a plot in the configured format (SVG or PNG).
    
    Args:
        fig: matplotlib Figure object
        filepath: Path to save (without extension, or with .png/.svg)
        tight: Whether to use tight bounding box
        
    Example:
        fig, ax = plt.subplots()
        ax.plot(x, y)
        save_plot(fig, 'plots/my_plot')  # Saves as my_plot.svg
    """
    from pathlib import Path
    filepath = Path(filepath)
    
    # Replace extension with configured format
    if filepath.suffix.lower() in ['.png', '.svg', '.pdf']:
        filepath = filepath.with_suffix(f'.{EXPORT_FORMAT}')
    else:
        filepath = Path(f"{filepath}.{EXPORT_FORMAT}")
    
    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    bbox = 'tight' if tight else None
    if EXPORT_FORMAT == 'svg':
        fig.savefig(filepath, format='svg', bbox_inches=bbox)
    else:
        fig.savefig(filepath, format='png', dpi=EXPORT_DPI, bbox_inches=bbox)
    
    return filepath


def get_color(name):
    """
    Returns a color from the central palette.
    
    Args:
        name: Color name (e.g., 'fairness', 'excitement', 'best')
        
    Returns:
        Hex color code as string
        
    Example:
        color = get_color('fairness')  # '#2E86AB'
    """
    return COLORS.get(name, COLORS['secondary_4'])


def get_colors(n):
    """
    Returns n colors from the palette.
    
    Args:
        n: Number of colors needed
        
    Returns:
        List of hex color codes
        
    Example:
        colors = get_colors(3)  # ['#2E86AB', '#E94F37', '#F39237']
    """
    if n <= len(COLOR_PALETTE):
        return COLOR_PALETTE[:n]
    else:
        # If more colors needed, repeat the palette
        return (COLOR_PALETTE * (n // len(COLOR_PALETTE) + 1))[:n]


def get_label(key):
    """
    Returns the English label for a given key.
    
    Args:
        key: Label key (e.g., 'win_rate', 'trick_changes')
        
    Returns:
        English label string
    """
    return LABELS.get(key, key)


def get_cmap(name='default'):
    """
    Returns a colormap for continuous data.
    
    Args:
        name: 'default', 'fairness', 'excitement', 'diverging'
        
    Returns:
        matplotlib Colormap
        
    Example:
        cmap = get_cmap('fairness')
        plt.scatter(x, y, c=values, cmap=cmap)
    """
    if name == 'fairness':
        # Blue-based colormap
        return mcolors.LinearSegmentedColormap.from_list(
            'fairness_cmap', 
            ['#FFFFFF', COLORS['fairness']]
        )
    elif name == 'excitement':
        # Red-based colormap
        return mcolors.LinearSegmentedColormap.from_list(
            'excitement_cmap', 
            ['#FFFFFF', COLORS['excitement']]
        )
    elif name == 'diverging':
        # Diverging colormap (Blue - White - Red)
        return mcolors.LinearSegmentedColormap.from_list(
            'diverging_cmap', 
            [COLORS['fairness'], '#FFFFFF', COLORS['excitement']]
        )
    else:
        # Default: Viridis-like
        return plt.cm.viridis


def create_pareto_plot(ax, x_validated, y_validated, x_fast=None, y_fast=None,
                       selected_points=None, title='Pareto Front'):
    """
    Creates a standardized Pareto front plot.
    
    Args:
        ax: matplotlib Axes
        x_validated: Win rates of validated front
        y_validated: Trick changes of validated front
        x_fast: (optional) Win rates of fast front
        y_fast: (optional) Trick changes of fast front
        selected_points: (optional) Dict with selected points
                        {'name': (win_rate, trick_changes), ...}
        title: Plot title
        
    Example:
        fig, ax = plt.subplots()
        create_pareto_plot(ax, win_rates, trick_changes,
                          selected_points={'Knee': (0.8, 3.5)})
    """
    # Fast front (if available)
    if x_fast is not None and y_fast is not None:
        ax.scatter(x_fast, y_fast, 
                  c=COLORS['pareto_fast'], 
                  alpha=0.3, 
                  s=50, 
                  label=LABELS['fast'])
    
    # Validated front
    ax.scatter(x_validated, y_validated, 
              c=COLORS['pareto_validated'], 
              s=100, 
              edgecolors='white',
              linewidths=1.5,
              label=LABELS['validated'],
              zorder=5)
    
    # Connecting line
    sorted_idx = np.argsort(x_validated)
    ax.plot(x_validated[sorted_idx], y_validated[sorted_idx], 
           c=COLORS['pareto_validated'], 
           alpha=0.5, 
           linestyle='--',
           linewidth=1.5)
    
    # Mark selected points
    if selected_points:
        markers = {'Fairness-Max': 's', 'Excitement-Max': '^', 'Knee-Point': 'D'}
        for name, (x, y) in selected_points.items():
            color = DECK_COLORS.get(name, COLORS['highlight'])
            marker = markers.get(name, 'o')
            ax.scatter(x, y, 
                      c=color, 
                      s=200, 
                      marker=marker,
                      edgecolors='black',
                      linewidths=2,
                      label=name,
                      zorder=10)
    
    ax.set_xlabel(LABELS['win_rate'])
    ax.set_ylabel(LABELS['trick_changes'])
    ax.set_title(title)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)


def create_comparison_bars(ax, labels, values_1, values_2, 
                           label_1='Fairness', label_2='Excitement',
                           title='Comparison'):
    """
    Creates a bar chart for comparisons.
    
    Args:
        ax: matplotlib Axes
        labels: List of categories
        values_1: Values for first series
        values_2: Values for second series
        label_1, label_2: Legend labels
        title: Plot title
    """
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, values_1, width, 
                   label=label_1, color=COLORS['fairness'])
    bars2 = ax.bar(x + width/2, values_2, width, 
                   label=label_2, color=COLORS['excitement'])
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


# =============================================================================
# EXAMPLE USAGE (for documentation)
# =============================================================================

if __name__ == '__main__':
    print("Plot configuration loaded.")
    print(f"\nSimulation parameters: R_FAST={R_FAST}, R_FINAL={R_FINAL}")
    print(f"Export format: {EXPORT_FORMAT.upper()}")
    print(f"Font sizes: Title={PLOT_STYLE['axes.titlesize']}, Labels={PLOT_STYLE['axes.labelsize']}, Legend={PLOT_STYLE['legend.fontsize']}")
    
    print("\nAvailable colors:")
    for name, color in COLORS.items():
        print(f"  {name}: {color}")
    
    print("\nUsage in notebooks:")
    print("""
    # At the beginning of the notebook:
    from plot_config import (
        COLORS, COLOR_PALETTE, ALGO_COLORS, DECK_COLORS, LABELS,
        R_FAST, R_FINAL, EXPORT_FORMAT,
        setup_plot_style, get_color, get_colors, get_label, get_cmap,
        save_plot, create_pareto_plot, create_comparison_bars
    )
    setup_plot_style()
    
    # Saving plots (automatically uses SVG):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    save_plot(fig, PLOTS_DIR / 'my_plot')  # Saves as my_plot.svg
    """)
