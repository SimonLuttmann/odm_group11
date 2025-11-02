"""
This module contains gradient-based optimization algorithms:
- SGD (Stochastic Gradient Descent)
- Momentum
- RMSProp
- Adam
"""

import numpy as np


def sgd(bb, objective, x0, learning_rate=0.01, max_iter=1000, tol=1e-6):
    """
    Stochastic Gradient Descent optimizer.
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        learning_rate: Step size
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    x = np.array(x0, dtype=float)
    history = []
    
    for i in range(max_iter):
        # Evaluate function and gradient
        f_val = bb.evaluate(objective, x.tolist())
        grad = np.array(bb.evaluate_gradient(objective, x.tolist()))
        
        history.append((i, x.copy(), f_val))
        
        # Check convergence
        if np.linalg.norm(grad) < tol:
            print(f"Converged after {i} iterations")
            break
        
        # Update step
        x = x - learning_rate * grad
    
    return x, history


def momentum(bb, objective, x0, learning_rate=0.01, beta=0.9, max_iter=1000, tol=1e-6):
    """
    Gradient Descent with Momentum optimizer.
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        learning_rate: Step size
        beta: Momentum coefficient (typically 0.9)
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    x = np.array(x0, dtype=float)
    v = np.zeros_like(x)  # Velocity
    history = []
    
    for i in range(max_iter):
        # Evaluate function and gradient
        f_val = bb.evaluate(objective, x.tolist())
        grad = np.array(bb.evaluate_gradient(objective, x.tolist()))
        
        history.append((i, x.copy(), f_val))
        
        # Check convergence
        if np.linalg.norm(grad) < tol:
            print(f"Converged after {i} iterations")
            break
        
        # Update velocity and position
        v = beta * v + learning_rate * grad
        x = x - v
    
    return x, history


def rmsprop(bb, objective, x0, learning_rate=0.01, beta=0.9, epsilon=1e-8, max_iter=1000, tol=1e-6):
    """
    RMSProp optimizer.
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        learning_rate: Step size
        beta: Decay rate for moving average (typically 0.9)
        epsilon: Small constant for numerical stability
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    x = np.array(x0, dtype=float)
    s = np.zeros_like(x)  # Running average of squared gradients
    history = []
    
    for i in range(max_iter):
        # Evaluate function and gradient
        f_val = bb.evaluate(objective, x.tolist())
        grad = np.array(bb.evaluate_gradient(objective, x.tolist()))
        
        history.append((i, x.copy(), f_val))
        
        # Check convergence
        if np.linalg.norm(grad) < tol:
            print(f"Converged after {i} iterations")
            break
        
        # Update running average of squared gradients
        s = beta * s + (1 - beta) * grad**2
        
        # Update parameters
        x = x - learning_rate * grad / (np.sqrt(s) + epsilon)
    
    return x, history


def adam(bb, objective, x0, learning_rate=0.01, beta1=0.9, beta2=0.999, epsilon=1e-8, max_iter=1000, tol=1e-6):
    """
    Adam optimizer (Adaptive Moment Estimation).
    
    Args:
        bb: BlackBox instance
        objective: Name of the objective function
        x0: Initial point (list or array)
        learning_rate: Step size (alpha)
        beta1: Exponential decay rate for first moment (typically 0.9)
        beta2: Exponential decay rate for second moment (typically 0.999)
        epsilon: Small constant for numerical stability
        max_iter: Maximum number of iterations
        tol: Tolerance for convergence
    
    Returns:
        x: Optimized parameters
        history: List of (iteration, x, f(x)) tuples
    """
    x = np.array(x0, dtype=float)
    m = np.zeros_like(x)  # First moment (mean)
    v = np.zeros_like(x)  # Second moment (uncentered variance)
    history = []
    
    for i in range(max_iter):
        # Evaluate function and gradient
        f_val = bb.evaluate(objective, x.tolist())
        grad = np.array(bb.evaluate_gradient(objective, x.tolist()))
        
        history.append((i, x.copy(), f_val))
        
        # Check convergence
        if np.linalg.norm(grad) < tol:
            print(f"Converged after {i} iterations")
            break
        
        # Update biased first and second moments
        m = beta1 * m + (1 - beta1) * grad
        v = beta2 * v + (1 - beta2) * grad**2
        
        # Bias correction
        m_hat = m / (1 - beta1**(i + 1))
        v_hat = v / (1 - beta2**(i + 1))
        
        # Update parameters
        x = x - learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)
    
    return x, history
