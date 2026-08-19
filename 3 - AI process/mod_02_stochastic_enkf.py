import numpy as np
from collections import deque

# --- MODULE 2 & 3: EULER-MARUYAMA DYNAMICS & DUAL STATE-PARAMETER ENSEMBLE KALMAN FILTER ---

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
    Dual State-Parameter Ensemble Kalman Filter (EnKF) with N = 50 ensemble members.
    Augmented state vector: z_t = [X_t, Y_t, alpha_t, beta_t, delta_t, gamma_t]^T (6D).
    Assimilates live YOLO prey count observations to estimate state densities, parameter values,
    bifurcation collapse risks, and interactive environmental stress tests.
    """
    def __init__(self, num_members=50, init_prey=10.0, init_predator=8.0, R_noise=4.0, history_len=100):
        self.N = num_members
        self.R = float(R_noise)
        self.H = np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
        
        prey_ensemble = np.maximum(0.1, np.random.normal(init_prey, 2.0, self.N))
        predator_ensemble = np.maximum(0.1, np.random.normal(init_predator, 2.0, self.N))
        
        # Initial prior parameter ensembles (6D state vector)
        alpha_ens = np.clip(np.random.normal(0.10, 0.01, self.N), 0.01, 0.5)
        beta_ens = np.clip(np.random.normal(0.02, 0.003, self.N), 0.001, 0.1)
        delta_ens = np.clip(np.random.normal(0.01, 0.002, self.N), 0.001, 0.1)
        gamma_ens = np.clip(np.random.normal(0.10, 0.01, self.N), 0.01, 0.5)
        
        self.ensemble = np.vstack([
            prey_ensemble, predator_ensemble,
            alpha_ens, beta_ens, delta_ens, gamma_ens
        ])
        
        self.history_len = history_len
        self.time_history = deque(maxlen=history_len)
        self.prey_history = deque(maxlen=history_len)
        self.predator_history = deque(maxlen=history_len)
        self.risk_history = deque(maxlen=history_len)
        self.bifurcation_history = deque(maxlen=history_len)
        self.alpha_history = deque(maxlen=history_len)
        self.beta_history = deque(maxlen=history_len)
        
        self.step_counter = 0
        self.active_shock_name = "NORMAL"

    @property
    def x(self):
        """Returns mean state vector (6, 1) of ensemble."""
        return np.mean(self.ensemble, axis=1, keepdims=True)

    def inject_environmental_shock(self, shock_type="heatwave"):
        """
        Injects real-time environmental disturbance shock into live EnKF parameter particles.
        Types: 'heatwave', 'pollution', 'invasive_predator', 'reset'
        """
        st = shock_type.lower()
        if st == "heatwave":
            self.ensemble[0, :] *= 0.7  # Thermal stress drops prey population
            self.ensemble[5, :] *= 1.4  # Increases mortality rate gamma
            self.active_shock_name = "HEATWAVE"
        elif st == "pollution":
            self.ensemble[0, :] *= 0.5  # Silt/toxic spill cuts prey
            self.ensemble[2, :] *= 0.6  # Reduces growth rate alpha
            self.active_shock_name = "POLLUTION"
        elif st == "invasive_predator":
            self.ensemble[1, :] *= 1.8  # Invasive predator influx
            self.ensemble[3, :] *= 1.5  # Increases predation rate beta
            self.active_shock_name = "INVASIVE"
        elif st == "reset":
            self.ensemble[2, :] = 0.10
            self.ensemble[3, :] = 0.02
            self.ensemble[4, :] = 0.01
            self.ensemble[5, :] = 0.10
            self.active_shock_name = "NORMAL"

    def compute_bifurcation_risk(self):
        """
        Calculates Early Warning Bifurcation Index based on Critical Slowing Down:
        - Lag-1 autocorrelation AR(1) over recent prey history
        - Spatial particle variance across ensemble
        """
        if len(self.prey_history) < 15:
            return 0.0
            
        recent = np.array(list(self.prey_history)[-20:])
        var = np.var(recent)
        
        # Lag-1 autocorrelation
        r_mean = np.mean(recent)
        num = np.sum((recent[:-1] - r_mean) * (recent[1:] - r_mean))
        den = np.sum((recent - r_mean) ** 2)
        ar1 = (num / den) if den > 1e-6 else 0.0
        
        # Combine variance and AR(1) into percentage [0 - 100%]
        risk_raw = max(0.0, ar1) * 60.0 + min(40.0, var * 10.0)
        return float(np.clip(risk_raw, 0.0, 100.0))

    def run_monte_carlo_stress_projection(self, steps=30, dt=0.1):
        """
        Runs 30-step forward Monte Carlo stress simulation using current estimated parameter distributions.
        Returns array of projected prey means and 95% confidence intervals.
        """
        proj_ensemble = self.ensemble.copy()
        proj_prey_means = []
        proj_risk = []
        
        for s in range(steps):
            X_f, Y_f = euler_maruyama_step(
                proj_ensemble[0, :], proj_ensemble[1, :],
                dt=dt, alpha=proj_ensemble[2, :], beta=proj_ensemble[3, :],
                gamma=proj_ensemble[5, :], delta=proj_ensemble[4, :]
            )
            proj_ensemble[0, :] = X_f
            proj_ensemble[1, :] = Y_f
            proj_prey_means.append(np.mean(X_f))
            ext_pct = (np.sum(X_f <= 2.0) / self.N) * 100.0
            proj_risk.append(ext_pct)
            
        return np.array(proj_prey_means), np.array(proj_risk)

    def step(self, live_yolo_prey_count, dt=0.1, sigma_x=0.05, sigma_y=0.05):
        """
        Executes one full 6D Dual State-Parameter Forecast-Update cycle of the EnKF.
        """
        self.step_counter += 1
        
        # 1. PARAMETER RANDOM-WALK PERTURBATION (Prevents parameter degeneracy)
        self.ensemble[2, :] += np.random.normal(0, 0.001, self.N)  # alpha
        self.ensemble[3, :] += np.random.normal(0, 0.0005, self.N) # beta
        self.ensemble[4, :] += np.random.normal(0, 0.0003, self.N) # delta
        self.ensemble[5, :] += np.random.normal(0, 0.001, self.N)  # gamma
        
        self.ensemble[2, :] = np.clip(self.ensemble[2, :], 0.01, 0.8)
        self.ensemble[3, :] = np.clip(self.ensemble[3, :], 0.001, 0.3)
        self.ensemble[4, :] = np.clip(self.ensemble[4, :], 0.001, 0.3)
        self.ensemble[5, :] = np.clip(self.ensemble[5, :], 0.01, 0.8)
        
        # 2. FORECAST STEP
        X_f, Y_f = euler_maruyama_step(
            self.ensemble[0, :], self.ensemble[1, :],
            dt=dt, alpha=self.ensemble[2, :], beta=self.ensemble[3, :],
            gamma=self.ensemble[5, :], delta=self.ensemble[4, :],
            sigma_x=sigma_x, sigma_y=sigma_y
        )
        
        forecast_ensemble = np.vstack([
            X_f, Y_f,
            self.ensemble[2, :], self.ensemble[3, :],
            self.ensemble[4, :], self.ensemble[5, :]
        ])
        
        mean_forecast = np.mean(forecast_ensemble, axis=1, keepdims=True)
        anomaly = forecast_ensemble - mean_forecast
        Pf = (anomaly @ anomaly.T) / (self.N - 1)
        
        # 3. OBSERVATION UPDATE (Prey count observation)
        z_k = float(live_yolo_prey_count)
        S = Pf[0, 0] + self.R
        K = Pf[:, [0]] / S if S > 0 else np.zeros((6, 1))
        
        v_i = np.random.normal(0.0, np.sqrt(self.R), size=self.N)
        perturbed_obs = z_k + v_i
        
        innovation = perturbed_obs - forecast_ensemble[0, :]
        updated_ensemble = forecast_ensemble + K @ innovation.reshape(1, self.N)
        
        updated_ensemble[0, :] = np.maximum(0.01, updated_ensemble[0, :])
        updated_ensemble[1, :] = np.maximum(0.01, updated_ensemble[1, :])
        updated_ensemble[2, :] = np.clip(updated_ensemble[2, :], 0.01, 0.8)
        updated_ensemble[3, :] = np.clip(updated_ensemble[3, :], 0.001, 0.3)
        updated_ensemble[4, :] = np.clip(updated_ensemble[4, :], 0.001, 0.3)
        updated_ensemble[5, :] = np.clip(updated_ensemble[5, :], 0.01, 0.8)
        
        self.ensemble = updated_ensemble
        
        # 4. EXTINCTION & BIFURCATION METRICS
        prey_states = self.ensemble[0, :]
        predator_states = self.ensemble[1, :]
        
        extinction_count = np.sum(prey_states <= 2.0)
        extinction_risk_pct = (extinction_count / self.N) * 100.0
        
        self.time_history.append(self.step_counter * dt)
        self.prey_history.append(np.mean(prey_states))
        self.predator_history.append(np.mean(predator_states))
        self.risk_history.append(extinction_risk_pct)
        self.alpha_history.append(np.mean(self.ensemble[2, :]))
        self.beta_history.append(np.mean(self.ensemble[3, :]))
        
        bif_risk = self.compute_bifurcation_risk()
        self.bifurcation_history.append(bif_risk)
        
        return {
            "prey_mean": np.mean(prey_states),
            "predator_mean": np.mean(predator_states),
            "extinction_risk": extinction_risk_pct,
            "bifurcation_risk": bif_risk,
            "est_alpha": np.mean(self.ensemble[2, :]),
            "est_beta": np.mean(self.ensemble[3, :]),
            "est_delta": np.mean(self.ensemble[4, :]),
            "est_gamma": np.mean(self.ensemble[5, :]),
            "active_shock": self.active_shock_name
        }

