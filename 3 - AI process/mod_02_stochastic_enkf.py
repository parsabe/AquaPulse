import numpy as np
from collections import deque

# --- MODULE 2 & 3: EULER-MARUYAMA DYNAMICS & ENSEMBLE KALMAN FILTER (EnKF) ---

def euler_maruyama_step(X, Y, dt=0.1, alpha=0.1, beta=0.02, gamma=0.1, delta=0.01, sigma_x=0.05, sigma_y=0.05):
    """
    Computes a single Euler-Maruyama discrete time step for the stochastic Lotka-Volterra model.
    Prey (X_n):      X_{n+1} = X_n + dt*(alpha*X_n - beta*X_n*Y_n) + sqrt(dt)*sigma_x*X_n*zeta_x
    Predator (Y_n):  Y_{n+1} = Y_n + dt*(delta*X_n*Y_n - gamma*Y_n) + sqrt(dt)*sigma_y*Y_n*zeta_y
    """
    zeta_x = np.random.normal(0, 1, size=np.shape(X))
    zeta_y = np.random.normal(0, 1, size=np.shape(Y))
    
    dX = dt * (alpha * X - beta * X * Y) + np.sqrt(dt) * sigma_x * X * zeta_x
    dY = dt * (delta * X * Y - gamma * Y) + np.sqrt(dt) * sigma_y * Y * zeta_y
    
    X_next = np.maximum(0.01, X + dX)
    Y_next = np.maximum(0.01, Y + dY)
    
    return X_next, Y_next


class EnsembleKalmanFilter:
    """
    Ensemble Kalman Filter (EnKF) with N = 50 ensemble members.
    Assimilates live YOLO prey count observations to estimate hidden predator dynamics and extinction risk.
    """
    def __init__(self, num_members=50, init_prey=10.0, init_predator=8.0, R_noise=4.0, history_len=100):
        self.N = num_members
        self.R = float(R_noise)
        self.H = np.array([[1.0, 0.0]])
        
        prey_ensemble = np.random.normal(init_prey, 2.0, self.N)
        predator_ensemble = np.random.normal(init_predator, 2.0, self.N)
        
        prey_ensemble = np.maximum(0.1, prey_ensemble)
        predator_ensemble = np.maximum(0.1, predator_ensemble)
        
        self.ensemble = np.vstack([prey_ensemble, predator_ensemble])
        
        self.history_len = history_len
        self.time_history = deque(maxlen=history_len)
        self.prey_history = deque(maxlen=history_len)
        self.predator_history = deque(maxlen=history_len)
        self.risk_history = deque(maxlen=history_len)
        
        self.step_counter = 0

    @property
    def x(self):
        """Returns mean state vector (2, 1) of ensemble."""
        return np.mean(self.ensemble, axis=1, keepdims=True)

    def step(self, live_yolo_prey_count, dt=0.1, alpha=0.1, beta=0.02, gamma=0.1, delta=0.01, sigma_x=0.05, sigma_y=0.05):
        """
        Executes one full Forecast-Update cycle of the EnKF.
        """
        self.step_counter += 1
        
        # 1. FORECAST STEP
        X_f, Y_f = euler_maruyama_step(
            self.ensemble[0, :], self.ensemble[1, :],
            dt=dt, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
            sigma_x=sigma_x, sigma_y=sigma_y
        )
        X_f = np.array(X_f, dtype=np.float64)
        Y_f = np.array(Y_f, dtype=np.float64)
        X_f_mean = np.mean(X_f)
        Y_f_mean = np.mean(Y_f)
        forecast_ensemble = np.vstack([X_f, Y_f])
        
        mean_forecast = np.array([[X_f_mean], [Y_f_mean]])
        anomaly = forecast_ensemble - mean_forecast
        Pf = (anomaly @ anomaly.T) / (self.N - 1)
        
        # 2. OBSERVATION STEP
        z_k = float(live_yolo_prey_count)
        
        # 3. UPDATE STEP
        S = Pf[0, 0] + self.R
        K = Pf[:, [0]] / S if S > 0 else np.zeros((2, 1))
        
        v_i = np.random.normal(0.0, np.sqrt(self.R), size=self.N)
        perturbed_obs = z_k + v_i
        
        innovation = perturbed_obs - forecast_ensemble[0, :]
        updated_ensemble = forecast_ensemble + K @ innovation.reshape(1, self.N)
        
        updated_ensemble[0, :] = np.maximum(0.01, updated_ensemble[0, :])
        updated_ensemble[1, :] = np.maximum(0.01, updated_ensemble[1, :])
        
        self.ensemble = updated_ensemble
        
        # 4. EXTINCTION METRIC & TELEMETRY
        prey_states = self.ensemble[0, :]
        predator_states = self.ensemble[1, :]
        
        extinction_count = np.sum(prey_states <= 2.0)
        extinction_risk_pct = (extinction_count / self.N) * 100.0
        
        self.time_history.append(self.step_counter * dt)
        self.prey_history.append(np.mean(prey_states))
        self.predator_history.append(np.mean(predator_states))
        self.risk_history.append(extinction_risk_pct)
        
        return {
            "prey_mean": np.mean(prey_states),
            "predator_mean": np.mean(predator_states),
            "extinction_risk": extinction_risk_pct
        }
