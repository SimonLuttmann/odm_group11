"""
This module contains direct search optimization algorithms:
- Coordinate Search
- Hooke & Jeeves Pattern Search
- Nelder-Mead Simplex Search
"""

import numpy as np


def coordinate_search(bb, objective, x0, step_size=0.1, reduction_factor=0.5, max_iter=1000, tol=1e-6):
    """
    Coordinate Search (Alternating Variables Method).
    Optimizes one coordinate at a time while keeping others fixed.
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        step_size: Initial step size for coordinate moves
        reduction_factor: Factor to reduce step size when no improvement
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence (step size threshold)
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    x = np.array(x0, dtype=float)
    n = len(x)
    current_step = step_size
    history = []
    iteration = 0
    
    while iteration < max_iter and current_step > tol:
        f_current = bb.evaluate(objective, x.tolist())
        history.append((iteration, x.copy(), f_current))
        
        improved = False
        
        # Try to improve along each coordinate
        for i in range(n):
            # Try positive direction
            x_temp = x.copy()
            x_temp[i] += current_step
            f_temp = bb.evaluate(objective, x_temp.tolist())
            
            if f_temp < f_current:
                x = x_temp
                f_current = f_temp
                improved = True
                continue
            
            # Try negative direction
            x_temp = x.copy()
            x_temp[i] -= current_step
            f_temp = bb.evaluate(objective, x_temp.tolist())
            
            if f_temp < f_current:
                x = x_temp
                f_current = f_temp
                improved = True
        
        # If no improvement, reduce step size
        if not improved:
            current_step *= reduction_factor
        
        iteration += 1

    print(f"Coordinate Search: {iteration} iterations")
    return x, history


def hooke_jeeves(bb, objective, x0, step_size=0.1, reduction_factor=0.5, max_iter=1000, tol=1e-6):
    """
    Hooke & Jeeves Pattern Search.
    Combines exploratory moves (coordinate search) with pattern moves (extrapolation).
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        step_size: Initial step size
        reduction_factor: Factor to reduce step size
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence (step size threshold)
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    def exploratory_search(x_base, current_step):
        """Perform exploratory moves around base point."""
        x = x_base.copy()
        n = len(x)
        f_base = bb.evaluate(objective, x.tolist())
        
        for i in range(n):
            # Try positive direction
            x_temp = x.copy()
            x_temp[i] += current_step
            f_temp = bb.evaluate(objective, x_temp.tolist())
            
            if f_temp < f_base:
                x = x_temp
                f_base = f_temp
            else:
                # Try negative direction
                x_temp = x.copy()
                x_temp[i] -= current_step
                f_temp = bb.evaluate(objective, x_temp.tolist())
                
                if f_temp < f_base:
                    x = x_temp
                    f_base = f_temp
        
        return x, f_base
    
    x_base = np.array(x0, dtype=float)
    current_step = step_size
    history = []
    iteration = 0
    
    f_base = bb.evaluate(objective, x_base.tolist())
    
    while iteration < max_iter and current_step > tol:
        history.append((iteration, x_base.copy(), f_base))
        
        # Exploratory search from base point
        x_new, f_new = exploratory_search(x_base, current_step)
        
        if f_new < f_base:
            # Pattern move: extrapolate in the successful direction
            x_pattern = x_new + (x_new - x_base)
            
            # Exploratory search from pattern point
            x_pattern_explored, f_pattern = exploratory_search(x_pattern, current_step)
            
            if f_pattern < f_new:
                # Pattern move was successful
                x_base = x_pattern_explored
                f_base = f_pattern
            else:
                # Pattern move failed, accept exploratory result
                x_base = x_new
                f_base = f_new
        else:
            # No improvement, reduce step size
            current_step *= reduction_factor
        
        iteration += 1
    
    print(f"Hooke & Jeeves: {iteration} iterations")
    return x_base, history


def nelder_mead(bb, objective, x0, max_iter=1000, tol=1e-6, alpha=1.0, gamma=2.0, rho=0.5, sigma=0.5):
    """
    Nelder-Mead Simplex Search.
    Maintains a simplex of n+1 points and transforms it using reflection, expansion, 
    contraction, and shrinkage operations.
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence (simplex size threshold)
        alpha: Reflection coefficient (default: 1.0)
        gamma: Expansion coefficient (default: 2.0)
        rho: Contraction coefficient (default: 0.5)
        sigma: Shrink coefficient (default: 0.5)
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    x0 = np.array(x0, dtype=float)
    n = len(x0)
    
    # Initialize simplex: n+1 points
    simplex = [x0.copy()]
    step = 0.1
    for i in range(n):
        x = x0.copy()
        x[i] += step
        simplex.append(x)
    
    # Evaluate function at simplex vertices
    f_values = [bb.evaluate(objective, x.tolist()) for x in simplex]
    
    history = []
    iteration = 0
    
    while iteration < max_iter:
        # Sort simplex by function values
        indices = np.argsort(f_values)
        simplex = [simplex[i] for i in indices]
        f_values = [f_values[i] for i in indices]
        
        # Best point
        x_best = simplex[0]
        f_best = f_values[0]
        
        history.append((iteration, x_best.copy(), f_best))
        
        # Check convergence: standard deviation of simplex
        simplex_array = np.array(simplex)
        if np.std(simplex_array) < tol:
            print(f"Nelder-Mead converged after {iteration} iterations")
            break
        
        # Centroid of all points except the worst
        centroid = np.mean(simplex[:-1], axis=0)
        
        # Reflection
        x_worst = simplex[-1]
        x_reflected = centroid + alpha * (centroid - x_worst)
        f_reflected = bb.evaluate(objective, x_reflected.tolist())
        
        if f_values[0] <= f_reflected < f_values[-2]:
            # Accept reflected point
            simplex[-1] = x_reflected
            f_values[-1] = f_reflected
        elif f_reflected < f_values[0]:
            # Try expansion
            x_expanded = centroid + gamma * (x_reflected - centroid)
            f_expanded = bb.evaluate(objective, x_expanded.tolist())
            
            if f_expanded < f_reflected:
                simplex[-1] = x_expanded
                f_values[-1] = f_expanded
            else:
                simplex[-1] = x_reflected
                f_values[-1] = f_reflected
        else:
            # Try contraction
            if f_reflected < f_values[-1]:
                # Outside contraction
                x_contracted = centroid + rho * (x_reflected - centroid)
            else:
                # Inside contraction
                x_contracted = centroid + rho * (x_worst - centroid)
            
            f_contracted = bb.evaluate(objective, x_contracted.tolist())
            
            if f_contracted < min(f_reflected, f_values[-1]):
                simplex[-1] = x_contracted
                f_values[-1] = f_contracted
            else:
                # Shrink simplex toward best point
                for i in range(1, n + 1):
                    simplex[i] = simplex[0] + sigma * (simplex[i] - simplex[0])
                    f_values[i] = bb.evaluate(objective, simplex[i].tolist())
        
        iteration += 1
    
    # Return the best point
    indices = np.argsort(f_values)
    x_best = simplex[indices[0]]
    print(f"Nelder-Mead: {iteration} iterations")
    
    return x_best, history
