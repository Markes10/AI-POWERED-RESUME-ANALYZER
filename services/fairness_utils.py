"""
Advanced Fairness utilities for Compensation Fairness Analyzer.

Features:
- Computes comprehensive pay equity metrics
- Detects potential bias using multiple fairness frameworks
- Statistical significance testing
- Intersectional fairness analysis
- Longitudinal trend analysis
"""
from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from scipy import stats
import warnings
from datetime import datetime, timedelta

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    _sklearn_available = True
except Exception:
    LinearRegression = None
    r2_score = None
    _sklearn_available = False

try:
    import pandas as pd
    _pandas_available = True
except Exception:
    pd = None
    _pandas_available = False

try:
    from fairlearn.metrics import (
        MetricFrame,
        selection_rate,
        demographic_parity_difference,
        equalized_odds_difference,
        true_positive_rate,
        false_positive_rate
    )
    from fairlearn.reductions import ExponentiatedGradient, DemographicParity
    _fairlearn_available = True
except ImportError:
    _fairlearn_available = False
    # Define placeholders so type annotations and references don't cause
    # NameError at import time when fairlearn is not installed.
    MetricFrame = None
    selection_rate = None
    demographic_parity_difference = None
    equalized_odds_difference = None
    true_positive_rate = None
    false_positive_rate = None
    ExponentiatedGradient = None
    DemographicParity = None

# Constants for statistical significance and effect size
ALPHA = 0.05  # Statistical significance threshold
COHEN_D_THRESHOLDS = {
    "small": 0.2,
    "medium": 0.5,
    "large": 0.8
}


# -------------------------------
# Core Statistical Utilities
# -------------------------------

def compute_statistical_significance(
    group1_data: List[float],
    group2_data: List[float]
) -> Dict[str, Any]:
    """
    Compute statistical significance and effect size between two groups.
    """
    # T-test for statistical significance
    t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
    
    # Cohen's d effect size
    n1, n2 = len(group1_data), len(group2_data)
    pooled_sd = np.sqrt(((n1-1)*np.var(group1_data) + (n2-1)*np.var(group2_data)) / (n1+n2-2))
    cohens_d = (np.mean(group1_data) - np.mean(group2_data)) / pooled_sd
    
    # Interpret effect size
    effect_size = "negligible"
    for threshold, label in [
        (COHEN_D_THRESHOLDS["large"], "large"),
        (COHEN_D_THRESHOLDS["medium"], "medium"),
        (COHEN_D_THRESHOLDS["small"], "small")
    ]:
        if abs(cohens_d) >= threshold:
            effect_size = label
            break
    
    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "effect_size": effect_size,
        "significant": p_value < ALPHA
    }

def _compute_group_statistics(
    salaries: List[float],
    indices: List[int],
    timestamps: Optional[List[datetime]] = None
) -> Dict[str, Any]:
    """Helper function to compute statistics for a group"""
    g_salaries = [salaries[i] for i in indices]
    
    stats_data = {
        "mean_salary": float(np.mean(g_salaries)),
        "median_salary": float(np.median(g_salaries)),
        "std_salary": float(np.std(g_salaries)),
        "count": len(g_salaries),
        "quartiles": [
            float(q) for q in np.percentile(g_salaries, [25, 50, 75])
        ]
    }
    
    if timestamps:
        g_times = [timestamps[i] for i in indices]
        stats_data["trend"] = compute_temporal_trend(g_salaries, g_times)
    
    return stats_data

def _compute_group_gaps(
    data: Dict[str, Any],
    salaries: List[float],
    groups: List[str],
    reference_stats: str,
    group_labels: set
) -> Dict[str, Any]:
    """Helper function to compute gaps between groups"""
    gaps = {}
    ref_salaries = [s for s, grp in zip(salaries, groups) if grp == reference_stats]
    
    for g in group_labels:
        if g != reference_stats:
            g_salaries = [s for s, grp in zip(salaries, groups) if grp == g]
            gap_pct = ((data[reference_stats]["median_salary"] - 
                       data[g]["median_salary"]) / 
                      data[reference_stats]["median_salary"] * 100)
            
            gaps[g] = {
                "gap_percentage": float(gap_pct),
                "statistical_significance": compute_statistical_significance(
                    ref_salaries, g_salaries
                ),
                "reference_group": reference_stats
            }
    
    return gaps

def compute_pay_gap(
    salaries: List[float],
    groups: List[str],
    timestamps: Optional[List[datetime]] = None
) -> Dict[str, Any]:
    """
    Enhanced pay gap analysis with statistical testing and trends.
    """
    data = {}
    group_labels = set(groups)
    reference_stats = None
    
    # Compute basic statistics for each group
    for g in group_labels:
        g_indices = [i for i, grp in enumerate(groups) if grp == g]
        if g_indices:
            stats_data = _compute_group_statistics(salaries, g_indices, timestamps)
            data[g] = stats_data
            
            # Use largest group as reference
            if (reference_stats is None or 
                stats_data["count"] > data[reference_stats]["count"]):
                reference_stats = g
    
    # Compute gaps and statistical significance
    gaps = {}
    if reference_stats and len(data) >= 2:
        gaps = _compute_group_gaps(data, salaries, groups, reference_stats, group_labels)

    return {
        "group_stats": data,
        "gaps": gaps,
        "reference_group": reference_stats
    }

def compute_bias_metrics(
    y_true: List[int],
    y_pred: List[int],
    sensitive_features: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Enhanced bias metrics with intersectional analysis.
    
    Args:
        y_true: Ground truth (0=low pay, 1=high pay)
        y_pred: Model predictions
        sensitive_features: Dict mapping feature names to values
    """
    if not _fairlearn_available:
        raise ImportError("Fairlearn not installed. Install with `pip install fairlearn`.")

    metrics = {
        "selection_rate": selection_rate,
        "demographic_parity": demographic_parity_difference,
        "equalized_odds": equalized_odds_difference,
        "true_positive_rate": true_positive_rate,
        "false_positive_rate": false_positive_rate
    }

    results = {}
    
    # Single feature analysis
    for feat_name, feat_values in sensitive_features.items():
        mf = MetricFrame(
            metrics=metrics,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features={feat_name: feat_values}
        )
        
        results[feat_name] = {
            "overall": {m: float(mf.overall[m]) for m in metrics},
            "by_group": {m: mf.by_group[m].to_dict() for m in metrics},
            "metric_significance": compute_metric_significance(mf)
        }

    # Intersectional analysis for pairs of features
    feature_names = list(sensitive_features.keys())
    if len(feature_names) >= 2:
        for i in range(len(feature_names)-1):
            for j in range(i+1, len(feature_names)):
                feat1, feat2 = feature_names[i], feature_names[j]
                
                # Create intersectional groups
                intersectional_features = [
                    f"{f1}_{f2}" 
                    for f1, f2 in zip(sensitive_features[feat1], 
                                    sensitive_features[feat2])
                ]
                
                mf = MetricFrame(
                    metrics=metrics,
                    y_true=y_true,
                    y_pred=y_pred,
                    sensitive_features={"intersection": intersectional_features}
                )
                
                results[f"{feat1}_x_{feat2}"] = {
                    "overall": {m: float(mf.overall[m]) for m in metrics},
                    "by_group": {m: mf.by_group[m].to_dict() for m in metrics},
                    "metric_significance": compute_metric_significance(mf)
                }
    
    return results

# -------------------------------
# Helper Functions
# -------------------------------

def compute_temporal_trend(
    values: List[float],
    timestamps: List[datetime]
) -> Dict[str, Any]:
    """Compute temporal trend in values"""
    # Convert timestamps to numerical values (days since first date)
    t0 = min(timestamps)
    days = [(t - t0).days for t in timestamps]
    
    # Fit linear regression (lazy import guard)
    if not _sklearn_available:
        raise ImportError("scikit-learn is required for temporal trend computation. Install with `pip install scikit-learn`")

    X = np.array(days).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression()
    model.fit(X, y)

    r2 = float(r2_score(y, model.predict(X)))
    slope = float(model.coef_[0])

    return {
        "slope": slope,  # Change per day
        "r2": r2,
        "trend_direction": "increasing" if slope > 0 else "decreasing",
        "significant": r2 > 0.6
    }

def compute_metric_significance(
    metric_frame: MetricFrame
) -> Dict[str, Dict[str, Any]]:
    """Compute statistical significance of metric differences"""
    significances = {}
    
    for metric in metric_frame.by_group.columns:
        values = metric_frame.by_group[metric]
        groups = list(values.index)
        
        # Compare each group to the overall metric
        overall = metric_frame.overall[metric]
        sig_results = {}
        
        for group in groups:
            group_val = values[group]
            diff = abs(group_val - overall)
            
            # Simple significance test based on effect size
            sig_results[group] = {
                "difference": float(diff),
                "significant": diff > 0.1,  # 10% threshold
                "direction": "above" if group_val > overall else "below"
            }
        
        significances[metric] = sig_results
    
    return significances

def generate_fairness_report(
    analysis_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a comprehensive fairness analysis report.
    
    Args:
        analysis_results: Combined results from .various fairness analyses
        report_format: Output format ("json" or "html")
    """
    report = {
        "summary": {
            "timestamp": datetime.now().isoformat(),
            "overall_fairness_score": calculate_overall_fairness_score(analysis_results),
            "critical_issues": [],
            "recommendations": []
        },
        "detailed_analysis": {
            "pay_equity": {},
            "bias_metrics": {},
            "trend_analysis": {},
            "intersectional_findings": {}
        },
        "visualizations": {
            "pay_distribution": None,
            "trend_charts": None,
            "fairness_metrics": None
        }
    }
    
    # Process pay equity findings
    if "pay_gap" in analysis_results:
        gaps = analysis_results["pay_gap"]
        report["detailed_analysis"]["pay_equity"] = {
            "gaps": gaps["gaps"],
            "statistical_significance": any(
                g["statistical_significance"]["significant"]
                for g in gaps["gaps"].values()
            ),
            "largest_gap": max(
                (g["gap_percentage"] for g in gaps["gaps"].values()),
                default=0
            )
        }
        
        if report["detailed_analysis"]["pay_equity"]["largest_gap"] > 5:
            report["summary"]["critical_issues"].append(
                "Significant pay gaps detected exceeding 5%"
            )
    
    # Process bias metrics
    if "bias_metrics" in analysis_results:
        metrics = analysis_results["bias_metrics"]
        report["detailed_analysis"]["bias_metrics"] = {
            attr: {
                "demographic_parity": metrics[attr]["overall"]["demographic_parity"],
                "equalized_odds": metrics[attr]["overall"]["equalized_odds"],
                "significant_disparities": [
                    m for m, v in metrics[attr]["metric_significance"].items()
                    if any(r["significant"] for r in v.values())
                ]
            }
            for attr in metrics
        }
    
    # Add trend analysis if available
    if "trends" in analysis_results:
        trends = analysis_results["trends"]
        report["detailed_analysis"]["trend_analysis"] = {
            "long_term_trends": identify_long_term_trends(trends),
            "seasonal_patterns": detect_seasonal_patterns(trends),
            "anomalies": detect_trend_anomalies(trends)
        }
    
    # Generate recommendations
    report["summary"]["recommendations"] = generate_smart_recommendations(
        report["detailed_analysis"]
    )
    
    return report

def calculate_overall_fairness_score(analysis_results: Dict[str, Any]) -> float:
    """
    Calculate an overall fairness score from .0 to 1 based on multiple metrics.
    """
    score_components = []
    weights = {
        "pay_gap": 0.4,
        "bias_metrics": 0.3,
        "trend": 0.3
    }
    
    # Evaluate pay gaps
    if "pay_gap" in analysis_results:
        gaps = analysis_results["pay_gap"]["gaps"]
        max_gap = max((abs(g["gap_percentage"]) for g in gaps.values()), default=0)
        gap_score = max(0, 1 - (max_gap / 20))  # Normalize by 20% threshold
        score_components.append(("pay_gap", gap_score))
    
    # Evaluate bias metrics
    if "bias_metrics" in analysis_results:
        bias_scores = []
        for attr_metrics in analysis_results["bias_metrics"].values():
            dp_score = 1 - abs(attr_metrics["overall"]["demographic_parity"])
            eo_score = 1 - abs(attr_metrics["overall"]["equalized_odds"])
            bias_scores.extend([dp_score, eo_score])
        if bias_scores:
            bias_score = np.mean(bias_scores)
            score_components.append(("bias_metrics", bias_score))
    
    # Evaluate trends
    if "trends" in analysis_results:
        trends = analysis_results["trends"]
        if "increasing_disparity" in trends:
            trend_score = 1 if not trends["increasing_disparity"] else 0.5
            score_components.append(("trend", trend_score))
    
    # Calculate weighted average
    if score_components:
        weighted_sum = sum(
            weights.get(component, 1) * score
            for component, score in score_components
        )
        total_weight = sum(
            weights.get(component, 1)
            for component, _ in score_components
        )
        return float(weighted_sum / total_weight)
    
    return 0.0

def identify_long_term_trends(
    trends: Dict[str, Any],
    min_periods: int = 4
) -> Dict[str, Any]:
    """
    Identify long-term trends in fairness metrics.
    """
    if not isinstance(trends, dict) or "historical_metrics" not in trends:
        return {"status": "insufficient_data"}
        
    metrics = trends["historical_metrics"]
    results = {}
    
    # Analyze each metric's trend
    for metric_name, values in metrics.items():
        if len(values) < min_periods:
            continue
            
        # Calculate trend direction and strength
        x = np.arange(len(values))
        y = np.array(values)
        slope, intercept = np.polyfit(x, y, 1)
        
        r_squared = 1 - (np.sum((y - (slope * x + intercept))**2) / 
                        np.sum((y - np.mean(y))**2))
        
        results[metric_name] = {
            "direction": "increasing" if slope > 0 else "decreasing",
            "strength": abs(slope),
            "significance": r_squared,
            "concerning": slope > 0 and r_squared > 0.7
        }
    
    return results

def detect_seasonal_patterns(
    trends: Dict[str, Any],
    period: int = 12  # Default to monthly data
) -> Dict[str, Any]:
    """
    Detect seasonal patterns in fairness metrics.
    """
    if not isinstance(trends, dict) or "historical_metrics" not in trends:
        return {"status": "insufficient_data"}
        
    metrics = trends["historical_metrics"]
    patterns = {}
    
    for metric_name, values in metrics.items():
        if len(values) < period * 2:  # Need at least 2 full cycles
            continue
            
        # Convert to numpy array
        data = np.array(values)
        
        # Calculate seasonal differences
        seasonal_diffs = []
        for i in range(len(data) - period):
            diff = data[i + period] - data[i]
            seasonal_diffs.append(diff)
            
        # Check for consistent patterns
        seasonal_diffs = np.array(seasonal_diffs)
        consistency = np.std(seasonal_diffs) / np.mean(np.abs(seasonal_diffs))
        
        patterns[metric_name] = {
            "seasonal_effect": float(np.mean(seasonal_diffs)),
            "consistency": float(1 / (1 + consistency)),
            "significant": consistency < 0.5
        }
    
    return patterns

def detect_trend_anomalies(
    trends: Dict[str, Any],
    z_threshold: float = 2.0
) -> Dict[str, Any]:
    """
    Detect anomalies in fairness metric trends.
    """
    if not isinstance(trends, dict) or "historical_metrics" not in trends:
        return {"status": "insufficient_data"}
        
    metrics = trends["historical_metrics"]
    anomalies = {}
    
    for metric_name, values in metrics.items():
        if len(values) < 3:  # Need at least 3 points
            continue
            
        data = np.array(values)
        mean = np.mean(data)
        std = np.std(data)
        
        # Detect points beyond z-threshold
        z_scores = np.abs((data - mean) / std)
        anomaly_points = np.nonzero(z_scores > z_threshold)[0]
        
        if len(anomaly_points) > 0:
            anomalies[metric_name] = {
                "indices": [int(i) for i in anomaly_points],
                "values": [float(data[i]) for i in anomaly_points],
                "z_scores": [float(z_scores[i]) for i in anomaly_points]
            }
    
    return anomalies

def generate_smart_recommendations(
    analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate smart, context-aware recommendations based on analysis results.
    """
    recommendations = []
    
    # Check pay equity issues
    if "pay_equity" in analysis:
        equity = analysis["pay_equity"]
        if equity.get("largest_gap", 0) > 5:
            recommendations.append({
                "category": "pay_equity",
                "priority": "high",
                "title": "Address Significant Pay Gaps",
                "description": "Significant pay gaps exceeding 5% detected",
                "actions": [
                    "Review compensation policies",
                    "Conduct pay adjustment analysis",
                    "Develop remediation plan"
                ],
                "impact": "high",
                "effort": "medium",
                "timeframe": "immediate"
            })
    
    # Check bias metrics
    if "bias_metrics" in analysis:
        for attr, metrics in analysis["bias_metrics"].items():
            if metrics["significant_disparities"]:
                recommendations.append({
                    "category": "bias_mitigation",
                    "priority": "high",
                    "title": f"Address {attr} Bias",
                    "description": f"Significant disparities detected in {attr}",
                    "actions": [
                        "Review decision processes",
                        "Implement bias mitigation strategies",
                        "Monitor outcomes closely"
                    ],
                    "impact": "high",
                    "effort": "high",
                    "timeframe": "short_term"
                })
    
    # Check trend issues
    if "trend_analysis" in analysis:
        trends = analysis["trend_analysis"]
        if trends.get("long_term_trends", {}).get("concerning", False):
            recommendations.append({
                "category": "trend_mitigation",
                "priority": "medium",
                "title": "Address Negative Trends",
                "description": "Concerning long-term trends detected",
                "actions": [
                    "Analyze root causes",
                    "Develop intervention strategy",
                    "Set up monitoring system"
                ],
                "impact": "medium",
                "effort": "medium",
                "timeframe": "medium_term"
            })
    
    return recommendations

def _analyze_model_performance(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    model_type: str
) -> Dict[str, Any]:
    """Helper function to analyze model performance metrics"""
    if model_type == "classification":
        from sklearn.metrics import classification_report
        y_pred = model.predict(X_test)
        return {"classification_report": classification_report(y_test, y_pred, output_dict=True)}
    else:
        from sklearn.metrics import r2_score, mean_squared_error
        y_pred = model.predict(X_test)
        return {
            "r2_score": float(r2_score(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred)))
        }

def _analyze_feature_importance(
    model: Any,
    features_array: np.ndarray,
    salary_array: np.ndarray
) -> Dict[str, Any]:
    """Helper function to analyze feature importance"""
    model.fit(features_array, salary_array)
    feature_importance = {
        f"feature_{i}": float(coef)
        for i, coef in enumerate(model.coef_)
    }
    return {
        "coefficients": feature_importance,
        "explained_variance": float(r2_score(salary_array, model.predict(features_array)))
    }

def _analyze_counterfactuals(
    features_array: np.ndarray,
    salary_array: np.ndarray,
    sensitive_attributes: Dict[str, np.ndarray]
) -> Dict[str, Dict[str, Any]]:
    """Helper function for counterfactual fairness analysis"""
    counterfactuals = {}
    if not _fairlearn_available:
        return counterfactuals
        
    for attr_name, attr_values in sensitive_attributes.items():
        unique_values = list(set(attr_values))
        cf_predictions = []
        
        for value in unique_values:
            cf_attrs = {
                k: v if k != attr_name else [value] * len(v)
                for k, v in sensitive_attributes.items()
            }
            
            cf_constraint = DemographicParity()
            cf_model = ExponentiatedGradient(
                LinearRegression(),
                constraints=cf_constraint,
                eps=0.01
            )
            cf_model.fit(features_array, salary_array, sensitive_features=cf_attrs[attr_name])
            cf_predictions.append(cf_model.predict(features_array))
        
        if cf_predictions:
            max_diff = float(max(np.mean(p) for p in cf_predictions) - 
                           min(np.mean(p) for p in cf_predictions))
            
            counterfactuals[attr_name] = {
                "counterfactual_disparity": max_diff,
                "interpretation": "high" if max_diff > 0.1 else "low"
            }
    
    return counterfactuals

def _generate_recommendations(
    feature_importance: Dict[str, Any],
    counterfactuals: Dict[str, Dict[str, Any]],
    bias_amplification: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Helper function to generate recommendations"""
    recommendations = []
    
    if feature_importance["explained_variance"] < 0.7:
        recommendations.append({
            "type": "structure",
            "priority": "high",
            "message": "Compensation structure lacks clear relationship with job-related factors"
        })
    
    high_disparity_attrs = [
        attr for attr, data in counterfactuals.items()
        if data["interpretation"] == "high"
    ]
    if high_disparity_attrs:
        recommendations.append({
            "type": "bias",
            "priority": "high",
            "message": f"High counterfactual disparity detected for: {', '.join(high_disparity_attrs)}"
        })
    
    increasing_bias_attrs = [
        attr for attr, data in bias_amplification.items()
        if data["increasing_disparity"]
    ]
    if increasing_bias_attrs:
        recommendations.append({
            "type": "trend",
            "priority": "medium",
            "message": f"Increasing disparities at higher salary levels for: {', '.join(increasing_bias_attrs)}"
        })
    
    return recommendations

def analyze_model_fairness(
    model: Any,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    sensitive_features: Dict[str, np.ndarray],
    model_type: str = "classification"
) -> Dict[str, Any]:
    """
    Analyze model fairness including feature importance, local explanations,
    and bias mitigation strategies.
    """
    try:
        import shap
        import lime
        import lime.lime_tabular
        _explanation_tools_available = True
    except ImportError:
        _explanation_tools_available = False

    results = {
        "model_performance": _analyze_model_performance(model, X_test, y_test, model_type),
        "feature_importance": _analyze_feature_importance(model, X_train, y_train),
        "counterfactual_analysis": _analyze_counterfactuals(X_train, y_train, sensitive_features),
        "bias_amplification": {},
        "recommendations": []
    }
    
    results["recommendations"] = _generate_recommendations(
        results["feature_importance"],
        results["counterfactual_analysis"],
        results["bias_amplification"]
    )
    
    return results
    
    # 1. Model Performance Analysis
    if model_type == "classification":
        from sklearn.metrics import classification_report
        y_pred = model.predict(X_test)
        results["model_performance"] = {
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }
    else:
        from sklearn.metrics import r2_score, mean_squared_error
        y_pred = model.predict(X_test)
        results["model_performance"] = {
            "r2_score": float(r2_score(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred)))
        }
    
    # 2. Feature Importance Analysis
    if _explanation_tools_available:
        # SHAP Analysis
        explainer = shap.TreeExplainer(model) if hasattr(model, "predict_proba") else shap.KernelExplainer(model.predict, X_train)
        shap_values = explainer.shap_values(X_test)
        
        if isinstance(shap_values, list):
            shap_values = np.array(shap_values).mean(axis=0)
        
        feature_importance = np.abs(shap_values).mean(axis=0)
        results["feature_importance"]["shap"] = {
            f"feature_{i}": float(imp)
            for i, imp in enumerate(feature_importance)
        }
        
        # LIME Analysis for sample points
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train,
            mode="classification" if model_type == "classification" else "regression"
        )
        
        # Get explanations for a few sample points
        sample_indices = np.random.choice(len(X_test), min(5, len(X_test)), replace=False)
        local_explanations = {}
        
        for idx in sample_indices:
            exp = lime_explainer.explain_instance(
                X_test[idx],
                model.predict_proba if model_type == "classification" else model.predict
            )
            local_explanations[f"sample_{idx}"] = {
                "feature_weights": exp.as_list(),
                "prediction": float(y_pred[idx]),
                "actual": float(y_test[idx])
            }
        
        results["local_explanations"] = local_explanations
    
    # 3. Comprehensive Bias Analysis
    bias_results = {}
    for attr_name, attr_values in sensitive_features.items():
        # Subgroup performance analysis
        unique_values = np.unique(attr_values)
        subgroup_performance = {}
        
        for value in unique_values:
            mask = attr_values == value
            if model_type == "classification":
                subgroup_perf = classification_report(
                    y_test[mask],
                    y_pred[mask],
                    output_dict=True
                )
            else:
                subgroup_perf = {
                    "r2": float(r2_score(y_test[mask], y_pred[mask])),
                    "rmse": float(np.sqrt(mean_squared_error(y_test[mask], y_pred[mask])))
                }
            subgroup_performance[str(value)] = subgroup_perf
        
        # Calculate disparate impact
        favorable_outcome = 1 if model_type == "classification" else np.median(y_pred)
        group_rates = {}
        
        for value in unique_values:
            mask = attr_values == value
            if model_type == "classification":
                rate = np.mean(y_pred[mask] == favorable_outcome)
            else:
                rate = np.mean(y_pred[mask] >= favorable_outcome)
            group_rates[str(value)] = float(rate)
        
        max_rate = max(group_rates.values())
        min_rate = min(group_rates.values())
        disparate_impact = min_rate / max_rate if max_rate > 0 else 1.0
        
        bias_results[attr_name] = {
            "subgroup_performance": subgroup_performance,
            "group_rates": group_rates,
            "disparate_impact": float(disparate_impact),
            "bias_detected": disparate_impact < 0.8
        }
    
    results["bias_analysis"] = bias_results
    
    # 4. Generate Mitigation Strategies
    for attr_name, bias_result in bias_results.items():
        if bias_result["bias_detected"]:
            strategies = []
            
            # Reweighting strategy
            if model_type == "classification":
                strategies.append({
                    "type": "reweighting",
                    "description": "Apply instance weights to balance outcomes across groups",
                    "implementation": {
                        "method": "compute_sample_weights",
                        "parameters": {
                            "sensitive_attribute": attr_name,
                            "target_metric": "demographic_parity"
                        }
                    }
                })
            
            # Threshold optimization
            strategies.append({
                "type": "threshold_optimization",
                "description": "Optimize decision thresholds per group",
                "implementation": {
                    "method": "optimize_thresholds",
                    "parameters": {
                        "sensitive_attribute": attr_name,
                        "metric": "equalized_odds"
                    }
                }
            })
            
            # Feature selection/engineering
            if _explanation_tools_available and "feature_importance" in results:
                high_impact_features = [
                    f for f, imp in results["feature_importance"]["shap"].items()
                    if imp > np.mean(list(results["feature_importance"]["shap"].values()))
                ]
                
                strategies.append({
                    "type": "feature_engineering",
                    "description": "Review and potentially modify high-impact features",
                    "implementation": {
                        "method": "review_features",
                        "parameters": {
                            "target_features": high_impact_features
                        }
                    }
                })
            
            results["mitigation_strategies"].extend(strategies)
    
    return results

def compute_attribute_distribution(
    data: Any,
    attribute: str
) -> Dict[str, float]:
    """
    Compute distribution of values for a given attribute.
    Returns dictionary mapping attribute values to their frequencies.
    """
    if isinstance(data, dict):
        if attribute in data:
            values = data[attribute]
        else:
            return {}
    else:
        try:
            values = data[attribute].values
        except:
            values = data[attribute]
    
    # Count occurrences
    from collections import Counter
    value_counts = Counter(values)
    total = sum(value_counts.values())
    
    # Convert to percentages
    return {
        str(val): count / total
        for val, count in value_counts.items()
    }

def compute_pay_gaps(
    data: Any,
    attribute: str,
    salary_column: str = "salary"
) -> Dict[str, float]:
    """
    Compute pay gaps for different groups within an attribute.
    Returns dictionary mapping groups to their pay gaps relative to the overall median.
    """
    if isinstance(data, dict):
        if attribute in data and salary_column in data:
            groups = data[attribute]
            salaries = data[salary_column]
        else:
            return {}
    else:
        try:
            groups = data[attribute].values
            salaries = data[salary_column].values
        except:
            return {}
    
    # Calculate overall median
    overall_median = float(np.median(salaries))
    
    # Calculate gaps by group
    gaps = {}
    unique_groups = set(groups)
    
    for group in unique_groups:
        group_salaries = [
            s for s, g in zip(salaries, groups)
            if g == group
        ]
        if group_salaries:
            group_median = float(np.median(group_salaries))
            gap = (overall_median - group_median) / overall_median
            gaps[str(group)] = gap
    
    return gaps

def analyze_causal_fairness(
    data: Any,
    treatment_column: str,
    outcome_column: str,
    protected_attributes: List[str],
    covariates: List[str]
) -> Dict[str, Any]:
    """
    Perform causal fairness analysis using DoWhy and EconML frameworks.
    
    Args:
        data: DataFrame containing all variables
        treatment_column: Name of treatment variable (e.g., "interview_score")
        outcome_column: Name of outcome variable (e.g., "salary")
        protected_attributes: List of protected attribute columns
        covariates: List of covariate columns for adjustment
    """
    try:
        import dowhy
        from dowhy import CausalModel
        import econml
        from econml.dml import CausalForestDML
        _causal_tools_available = True
    except ImportError:
        _causal_tools_available = False
        return {"error": "Causal analysis packages not available"}
        
    results = {
        "causal_effects": {},
        "heterogeneous_effects": {},
        "fairness_metrics": {},
        "recommendations": []
    }
    
    if not _causal_tools_available:
        return results
        
    # 1. Overall Causal Effect Analysis
    model = CausalModel(
        data=data,
        treatment=treatment_column,
        outcome=outcome_column,
        common_causes=covariates
    )
    
    # Identify causal effect
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
    estimate = model.estimate_effect(identified_estimand,
                                   method_name="backdoor.linear_regression")
    
    results["causal_effects"]["overall"] = {
        "ate": float(estimate.value),
        "confidence_intervals": [
            float(ci) for ci in estimate.get_confidence_intervals()
        ],
        "significance": float(estimate.value) / float(estimate.stderr) > 1.96
    }
    
    # 2. Heterogeneous Treatment Effect Analysis
    for attr in protected_attributes:
        # Estimate effects using Causal Forest
        cf_model = CausalForestDML(
            n_estimators=100,
            min_samples_leaf=10,
            max_depth=5,
            random_state=42
        )
        
        # Prepare features
        features = data[covariates + [attr]]
        treatment = data[treatment_column]
        outcome = data[outcome_column]
        
        # Fit model
        cf_model.fit(features, treatment, outcome)
        
        # Get treatment effects
        effects = cf_model.effect(features)
        
        # Analyze heterogeneity by protected attribute
        effects_by_group = {}
        for group in data[attr].unique():
            mask = data[attr] == group
            group_effects = effects[mask]
            effects_by_group[str(group)] = {
                "mean_effect": float(np.mean(group_effects)),
                "std_effect": float(np.std(group_effects)),
                "sample_size": int(sum(mask))
            }
        
        results["heterogeneous_effects"][attr] = effects_by_group
        
        # Calculate treatment effect disparity
        max_effect = max(g["mean_effect"] for g in effects_by_group.values())
        min_effect = min(g["mean_effect"] for g in effects_by_group.values())
        disparity = max_effect - min_effect
        
        results["fairness_metrics"][attr] = {
            "effect_disparity": float(disparity),
            "normalized_disparity": float(disparity / abs(results["causal_effects"]["overall"]["ate"]))
        }
    
    # 3. Generate Recommendations
    for attr, metrics in results["fairness_metrics"].items():
        if metrics["normalized_disparity"] > 0.1:  # 10% threshold
            results["recommendations"].append({
                "attribute": attr,
                "finding": "Significant heterogeneous treatment effects detected",
                "disparity_level": "high" if metrics["normalized_disparity"] > 0.2 else "medium",
                "actions": [
                    "Review decision-making processes for potential disparate impact",
                    "Consider group-specific interventions",
                    "Implement monitoring for treatment effect disparities"
                ]
            })
    
    return results

def analyze_model_robustness(
    model: Any,
    X_test: np.ndarray,
    protected_attributes: Dict[str, np.ndarray],
    eps: float = 0.1
) -> Dict[str, Any]:
    """
    Analyze model robustness and fairness under perturbations.
    
    Args:
        model: Trained ML model
        X_test: Test features
        protected_attributes: Protected attribute values
        eps: Perturbation size
    """
    try:
        from art.estimators.classification import SklearnClassifier
        from art.attacks.evasion import FastGradientMethod
        import captum.attr as captum
        _robustness_tools_available = True
    except ImportError:
        _robustness_tools_available = False
        return {"error": "Robustness analysis packages not available"}
    
    results = {
        "robustness_metrics": {},
        "attribution_analysis": {},
        "group_robustness": {},
        "recommendations": []
    }
    
    if not _robustness_tools_available:
        return results
    
    # 1. Adversarial Robustness Analysis
    classifier = SklearnClassifier(model)
    attack = FastGradientMethod(classifier, eps=eps)
    
    # Generate adversarial examples
    X_adv = attack.generate(X_test)
    
    # Analyze robustness by protected group
    for attr_name, attr_values in protected_attributes.items():
        group_robustness = {}
        for group in np.unique(attr_values):
            mask = attr_values == group
            
            # Original accuracy
            orig_acc = np.mean(
                model.predict(X_test[mask]) == model.predict(X_test[mask])
            )
            
            # Adversarial accuracy
            adv_acc = np.mean(
                model.predict(X_test[mask]) == model.predict(X_adv[mask])
            )
            
            group_robustness[str(group)] = {
                "original_accuracy": float(orig_acc),
                "adversarial_accuracy": float(adv_acc),
                "robustness_score": float(adv_acc / orig_acc if orig_acc > 0 else 0)
            }
        
        results["group_robustness"][attr_name] = group_robustness
    
    # 2. Attribution Analysis
    if hasattr(model, "predict_proba"):
        # Use Integrated Gradients for attribution
        ig = captum.IntegratedGradients(model)
        attributions = ig.attribute(X_test, target=model.predict(X_test))
        
        # Analyze feature importance by protected group
        for attr_name, attr_values in protected_attributes.items():
            group_attributions = {}
            for group in np.unique(attr_values):
                mask = attr_values == group
                group_attr = attributions[mask]
                
                group_attributions[str(group)] = {
                    "mean_attribution": float(np.mean(np.abs(group_attr))),
                    "top_features": [
                        int(i) for i in np.argsort(np.mean(np.abs(group_attr), axis=0))[-5:]
                    ]
                }
            
            results["attribution_analysis"][attr_name] = group_attributions
    
    # 3. Generate Recommendations
    for attr, rob_metrics in results["group_robustness"].items():
        min_rob = min(g["robustness_score"] for g in rob_metrics.values())
        if min_rob < 0.8:  # 80% robustness threshold
            results["recommendations"].append({
                "category": "robustness",
                "attribute": attr,
                "finding": "Low adversarial robustness detected",
                "severity": "high" if min_rob < 0.6 else "medium",
                "actions": [
                    "Implement adversarial training",
                    "Add robustness constraints to model training",
                    "Monitor model behavior under perturbations"
                ]
            })
    
    return results

def setup_fairness_monitoring(
    model_name: str,
    metrics_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Set up comprehensive monitoring of fairness metrics with production-ready features.
    
    Args:
        model_name: Name of the model to monitor
        metrics_config: Configuration for metrics to track
    """
    try:
        import mlflow
        try:
            import wandb
            _wandb_available = True
        except ImportError:
            wandb = None
            _wandb_available = False
        from evidently.dashboard import Dashboard
        from evidently.dashboard.tabs import (
            DataDriftTab, CatTargetDriftTab, RegressionPerformanceTab,
            ClassificationPerformanceTab, ProbClassificationPerformanceTab
        )
        from deepchecks.tabular import Dataset, Suite
        from deepchecks.tabular.checks import (
            WholeDatasetDrift, TrainTestFeatureDrift,
            FeatureAttributionDrift, ConceptDrift
        )
        import great_expectations as ge
        from datetime import datetime, timedelta
        import logging
        _monitoring_tools_available = True
    except ImportError:
        _monitoring_tools_available = False
        return {"error": "Monitoring packages not available"}
        
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{model_name}_fairness_monitoring.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(f"{model_name}_fairness_monitor")
        
    monitoring_config = {
        "tracking": {
            "mlflow": {
                "experiment_name": f"{model_name}_fairness_monitoring",
                "metrics": metrics_config.get("mlflow_metrics", []),
                "tags": {
                    "monitoring_type": "fairness",
                    "start_time": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            },
            "wandb": {
                "project": f"{model_name}_fairness",
                "metrics": metrics_config.get("wandb_metrics", []),
                "group": "fairness_monitoring",
                "job_type": "monitoring"
            }
        },
        "drift_detection": {
            "features": metrics_config.get("drift_features", []),
            "protected_attributes": metrics_config.get("protected_attributes", []),
            "thresholds": {
                "drift_threshold": metrics_config.get("drift_threshold", 0.05),
                "concept_drift_threshold": metrics_config.get("concept_drift_threshold", 0.1),
                "feature_importance_threshold": metrics_config.get("feature_importance_threshold", 0.2)
            }
        },
        "validation": {
            "expectations": metrics_config.get("expectations", []),
            "checks": metrics_config.get("checks", []),
            "data_quality": {
                "min_completeness": 0.95,
                "max_drift": 0.1,
                "bias_threshold": 0.05
            }
        },
        "alerts": {
            "email": metrics_config.get("alert_email"),
            "slack_webhook": metrics_config.get("slack_webhook"),
            "thresholds": {
                "critical": 0.2,
                "warning": 0.1,
                "info": 0.05
            },
            "cooldown_period": timedelta(hours=24)
        },
        "storage": {
            "metrics_retention": timedelta(days=90),
            "snapshots_enabled": True,
            "snapshot_frequency": timedelta(days=1)
        }
    }
    
    if _monitoring_tools_available:
        try:
            # MLflow advanced setup
            mlflow.set_experiment(monitoring_config["tracking"]["mlflow"]["experiment_name"])
            mlflow.set_tracking_uri(metrics_config.get("mlflow_tracking_uri", "sqlite:///mlflow.db"))
            
            # Set up MLflow experiment with tags
            experiment = mlflow.get_experiment_by_name(monitoring_config["tracking"]["mlflow"]["experiment_name"])
            if experiment is None:
                exp_id = mlflow.create_experiment(
                    monitoring_config["tracking"]["mlflow"]["experiment_name"],
                    tags=monitoring_config["tracking"]["mlflow"]["tags"]
                )
            else:
                exp_id = experiment.experiment_id
                mlflow.set_experiment_tag(exp_id, "last_updated", datetime.now().isoformat())
            
            # Wandb advanced setup
            wandb.init(
                project=monitoring_config["tracking"]["wandb"]["project"],
                group=monitoring_config["tracking"]["wandb"]["group"],
                job_type=monitoring_config["tracking"]["wandb"]["job_type"],
                config=monitoring_config,
                resume=True
            )
            
            # Set up Evidently dashboard with all relevant tabs
            dashboard = Dashboard(tabs=[
                DataDriftTab(),
                CatTargetDriftTab(),
                RegressionPerformanceTab(),
                ClassificationPerformanceTab(),
                ProbClassificationPerformanceTab()
            ])
            
            # Set up DeepChecks suite with comprehensive checks
            suite = Suite(
                "Fairness Monitoring Suite",
                [
                    WholeDatasetDrift(),
                    TrainTestFeatureDrift(),
                    FeatureAttributionDrift(),
                    ConceptDrift()
                ]
            )
            
            # Initialize Great Expectations
            context = ge.data_context.DataContext()
            
            # Create base expectation suite
            suite_name = f"{model_name}_fairness_suite"
            try:
                context.create_expectation_suite(suite_name, overwrite_existing=True)
                logger.info(f"Created Great Expectations suite: {suite_name}")
            except Exception as e:
                logger.error(f"Error creating expectation suite: {e}")
            
            logger.info(f"Successfully initialized monitoring for model: {model_name}")
        except Exception as e:
            logger.error(f"Error setting up monitoring: {e}")
            return {"error": f"Failed to set up monitoring: {str(e)}"}
    
    return monitoring_config

def monitor_fairness_metrics(
    data: Any,
    config: Dict[str, Any],
    current_metrics: Dict[str, Any],
    reference_data: Optional[Any] = None,
    model: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Enhanced production-ready monitoring of fairness metrics with comprehensive
    drift detection, validation, and alerting.
    
    Args:
        data: Current data batch
        config: Monitoring configuration
        current_metrics: Current fairness metrics
        reference_data: Optional reference/baseline data
        model: Optional model for performance monitoring
    """
    try:
        import mlflow
        import wandb
        from evidently.dashboard import Dashboard
        from evidently.dashboard.tabs import (
            DataDriftTab, CatTargetDriftTab, RegressionPerformanceTab,
            ClassificationPerformanceTab, ProbClassificationPerformanceTab,
            DataQualityTab
        )
        from deepchecks.tabular import Dataset, Suite
        from deepchecks.tabular.checks import (
            WholeDatasetDrift, TrainTestFeatureDrift,
            FeatureAttributionDrift, ConceptDrift,
            FeatureDrift, LabelDrift
        )
        import great_expectations as ge
        from river import drift
        import numpy as np
        import pandas as pd
        from datetime import datetime
        import json
        import logging
        import requests
        from typing import Dict, List, Any, Optional
        _monitoring_tools_available = True
    except ImportError:
        _monitoring_tools_available = False
        return {"error": "Monitoring packages not available"}
    
    # Set up logging
    logger = logging.getLogger("fairness_monitor")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "drift_detected": False,
        "alerts": [],
        "metrics_tracked": {},
        "validation_results": {},
        "data_quality": {},
        "performance_metrics": {},
        "feature_importance": {},
        "recommendations": []
    }
    
    if not _monitoring_tools_available:
        return results
    
    try:
        # 1. Enhanced Metric Tracking
        with mlflow.start_run(run_name=f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log current metrics
            for metric_name, value in current_metrics.items():
                if metric_name in config["tracking"]["mlflow"]["metrics"]:
                    mlflow.log_metric(metric_name, value)
                    results["metrics_tracked"][metric_name] = value
            
            # Log metadata
            mlflow.log_params({
                "monitoring_timestamp": datetime.now().isoformat(),
                "data_size": len(data) if hasattr(data, "__len__") else "unknown",
                "config_version": config.get("version", "1.0.0")
            })
        
        # Wandb logging with additional context
        wandb.log({
            **current_metrics,
            "monitoring_run": {
                "timestamp": datetime.now().isoformat(),
                "config": config
            }
        })
        
        # 2. Enhanced Drift Detection
        if isinstance(data, pd.DataFrame):
            drift_results = {}
            
            # Statistical drift detection
            if reference_data is not None:
                dashboard = Dashboard(tabs=[
                    DataDriftTab(),
                    CatTargetDriftTab(),
                    DataQualityTab()
                ])
                dashboard.calculate(reference_data, data)
                drift_results["statistical_drift"] = json.loads(dashboard.json())
            
            # Advanced drift detection per feature
            feature_drift = {}
            for feature in config["drift_detection"]["features"]:
                # ADWIN drift detector
                adwin_detector = drift.ADWIN(
                    delta=config["drift_detection"]["thresholds"]["drift_threshold"]
                )
                
                # Page Hinkley drift detector for confirmation
                ph_detector = drift.PageHinkley(
                    min_instances=30,
                    delta=config["drift_detection"]["thresholds"]["drift_threshold"],
                    threshold=10
                )
                
                feature_values = data[feature].values if isinstance(data, pd.DataFrame) else data[feature]
                
                drift_detected_adwin = False
                drift_detected_ph = False
                
                for val in feature_values:
                    if adwin_detector.update(val):
                        drift_detected_adwin = True
                    if ph_detector.update(val):
                        drift_detected_ph = True
                
                # Only report drift if both detectors agree
                if drift_detected_adwin and drift_detected_ph:
                    feature_drift[feature] = {
                        "drift_detected": True,
                        "confidence": "high" if adwin_detector.width > 100 else "medium",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    results["alerts"].append({
                        "type": "drift",
                        "feature": feature,
                        "severity": "high" if adwin_detector.width > 100 else "medium",
                        "message": f"Significant drift detected in feature {feature}",
                        "details": {
                            "adwin_width": adwin_detector.width,
                            "ph_change_magnitude": ph_detector.magnitude
                        }
                    })
                    results["drift_detected"] = True
            
            drift_results["feature_drift"] = feature_drift
            results["drift_analysis"] = drift_results
        
        # 3. Enhanced Validation with Multiple Frameworks
        validation_results = {}
        
        # Great Expectations validation
        try:
            context = ge.data_context.DataContext()
            suite_name = "fairness_monitoring_suite"
            
            # Create or get expectation suite
            try:
                suite = context.create_expectation_suite(suite_name)
            except:
                suite = context.get_expectation_suite(suite_name)
            
            # Add/update expectations
            for expectation in config["validation"]["expectations"]:
                suite.add_expectation(expectation)
            
            # Validate data
            if isinstance(data, pd.DataFrame):
                batch = context.get_batch(data, suite_name)
                validation_results["great_expectations"] = context.run_validation(
                    batch, suite
                )
        except Exception as e:
            logger.error(f"Great Expectations validation failed: {e}")
            validation_results["great_expectations"] = {"error": str(e)}
        
        # DeepChecks validation
        try:
            if isinstance(data, pd.DataFrame):
                dataset = Dataset(data)
                deepchecks_suite = Suite([
                    WholeDatasetDrift(),
                    TrainTestFeatureDrift(),
                    FeatureAttributionDrift(),
                    ConceptDrift(),
                    FeatureDrift(),
                    LabelDrift()
                ])
                
                check_results = deepchecks_suite.run(dataset)
                validation_results["deepchecks"] = check_results.to_dict()
        except Exception as e:
            logger.error(f"DeepChecks validation failed: {e}")
            validation_results["deepchecks"] = {"error": str(e)}
        
        results["validation_results"] = validation_results
        
        # 4. Enhanced Alert Generation
        alert_manager = AlertManager(config["alerts"])
        
        # Metric-based alerts
        for metric_name, value in current_metrics.items():
            if metric_name in config["tracking"]["mlflow"]["metrics"]:
                alert = alert_manager.check_metric(metric_name, value)
                if alert:
                    results["alerts"].append(alert)
        
        # Drift-based alerts
        if results["drift_detected"]:
            alert = alert_manager.create_drift_alert(results["drift_analysis"])
            if alert:
                results["alerts"].append(alert)
        
        # Validation-based alerts
        for framework, validation in results["validation_results"].items():
            if isinstance(validation, dict) and "error" not in validation:
                alert = alert_manager.check_validation(framework, validation)
                if alert:
                    results["alerts"].append(alert)
        
        # 5. Generate Recommendations
        recommendations = []
        
        # Drift-based recommendations
        if results["drift_detected"]:
            recommendations.append({
                "category": "drift",
                "priority": "high",
                "title": "Address Data Drift",
                "description": "Significant drift detected in monitored features",
                "actions": [
                    "Review feature distributions",
                    "Update model if necessary",
                    "Investigate root cause of drift"
                ]
            })
        
        # Validation-based recommendations
        if validation_results.get("deepchecks", {}).get("failed_checks", []):
            recommendations.append({
                "category": "validation",
                "priority": "medium",
                "title": "Address Failed Validation Checks",
                "description": "Some validation checks have failed",
                "actions": [
                    "Review failed checks",
                    "Update data quality processes",
                    "Consider model retraining"
                ]
            })
        
        results["recommendations"] = recommendations
        
        # 6. Send Alerts
        if config["alerts"].get("email") or config["alerts"].get("slack_webhook"):
            alert_manager.send_alerts(results["alerts"])
        
        # 7. Store Results
        if config["storage"]["snapshots_enabled"]:
            store_monitoring_snapshot(results, config["storage"])
        
        logger.info("Fairness monitoring completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error during fairness monitoring: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "partial_results": results
        }

class AlertManager:
    """Helper class for managing monitoring alerts"""
    
    def __init__(self, alert_config: Dict[str, Any]):
        self.config = alert_config
        self.last_alert_time = {}
    
    def check_metric(self, metric_name: str, value: float) -> Optional[Dict[str, Any]]:
        """Check if metric value should trigger an alert"""
        if abs(value) > self.config["thresholds"]["critical"]:
            return self._create_alert("critical", metric_name, value)
        elif abs(value) > self.config["thresholds"]["warning"]:
            return self._create_alert("warning", metric_name, value)
        return None
    
    def create_drift_alert(self, drift_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create alert for drift detection"""
        if drift_analysis.get("feature_drift"):
            return {
                "type": "drift",
                "severity": "high",
                "timestamp": datetime.now().isoformat(),
                "message": "Significant drift detected in multiple features",
                "details": drift_analysis
            }
        return None
    
    def check_validation(self, framework: str, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check validation results for alert conditions"""
        if framework == "great_expectations" and not results.get("success", True):
            return {
                "type": "validation",
                "severity": "high",
                "framework": framework,
                "message": "Data quality expectations not met",
                "details": results
            }
        return None
    
    def _create_alert(self, severity: str, metric_name: str, value: float) -> Dict[str, Any]:
        """Create standardized alert object"""
        return {
            "type": "metric",
            "severity": severity,
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "message": f"Metric {metric_name} exceeded {severity} threshold"
        }
    
    def send_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """Send alerts through configured channels"""
        for alert in alerts:
            # Check cooldown period
            alert_key = f"{alert['type']}_{alert.get('metric', '')}"
            last_time = self.last_alert_time.get(alert_key)
            
            if last_time and (datetime.now() - last_time) < self.config["cooldown_period"]:
                continue
            
            # Send email alert
            if self.config.get("email"):
                self._send_email_alert(alert)
            
            # Send Slack alert
            if self.config.get("slack_webhook"):
                self._send_slack_alert(alert)
            
            self.last_alert_time[alert_key] = datetime.now()
    
    def _send_email_alert(self, alert: Dict[str, Any]) -> None:
        """Send alert via email"""
        # Implement email sending logic here
        pass
    
    def _send_slack_alert(self, alert: Dict[str, Any]) -> None:
        """Send alert to Slack"""
        if self.config.get("slack_webhook"):
            try:
                requests.post(
                    self.config["slack_webhook"],
                    json={
                        "text": f"*Fairness Alert*\nType: {alert['type']}\nSeverity: {alert['severity']}\nMessage: {alert['message']}"
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")

def store_monitoring_snapshot(
    results: Dict[str, Any],
    storage_config: Dict[str, Any]
) -> None:
    """Store monitoring results for historical analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Save to JSON file
        with open(f"monitoring_snapshot_{timestamp}.json", "w") as f:
            json.dump(results, f)
        
        # Cleanup old snapshots based on retention period
        cleanup_old_snapshots(storage_config["metrics_retention"])
    except Exception as e:
        logger.error(f"Failed to store monitoring snapshot: {e}")

def cleanup_old_snapshots(retention_period: timedelta) -> None:
    """Remove monitoring snapshots older than retention period"""
    import glob
    import os
    
    cutoff_time = datetime.now() - retention_period
    
    for file in glob.glob("monitoring_snapshot_*.json"):
        try:
            file_time = datetime.strptime(
                file.split("_")[2].split(".")[0],
                "%Y%m%d%H%M%S"
            )
            if file_time < cutoff_time:
                os.remove(file)
        except Exception as e:
            logger.error(f"Failed to process snapshot file {file}: {e}")

def analyze_demographic_fairness(
    data: Dict[str, Any],
    region_code: str,
    year: int,
    protected_attributes: List[str]
) -> Dict[str, Any]:
    """
    Analyze fairness metrics against demographic benchmarks using census data.
    
    Args:
        data: Company compensation data
        region_code: Geographic region code for census data
        year: Year for census data comparison
        protected_attributes: List of protected attributes to analyze
    """
    try:
        from folktables import ACSDataSource, ACSEmployment
        _folktables_available = True
    except ImportError:
        _folktables_available = False
        return {"error": "Folktables package not available"}
    
    results = {
        "demographic_comparison": {},
        "representation_metrics": {},
        "wage_gap_analysis": {},
        "recommendations": []
    }
    
    if not _folktables_available:
        return results
        
    # Load ACS data
    data_source = ACSDataSource(survey_year=year, horizon='1-Year', survey='person')
    acs_data = data_source.get_data(states=[region_code], download=True)
    
    # Calculate demographic baselines
    employment_filter = ACSEmployment.target_filter(acs_data)
    acs_employment = acs_data[employment_filter]
    
    # Analyze representation
    for attr in protected_attributes:
        company_dist = compute_attribute_distribution(data, attr)
        census_dist = compute_attribute_distribution(acs_employment, attr)
        
        # Calculate representation scores
        representation = {
            group: {
                "company_pct": company_pct,
                "market_pct": census_dist.get(group, 0),
                "gap": company_pct - census_dist.get(group, 0)
            }
            for group, company_pct in company_dist.items()
        }
        
        results["representation_metrics"][attr] = {
            "distribution": representation,
            "summary": {
                "max_gap": max(abs(v["gap"]) for v in representation.values()),
                "underrepresented_groups": [
                    group for group, metrics in representation.items()
                    if metrics["gap"] < -0.05  # 5% threshold
                ]
            }
        }
    
    # Analyze wage gaps against market data
    for attr in protected_attributes:
        company_gaps = compute_pay_gaps(data, attr)
        market_gaps = compute_pay_gaps(acs_employment, attr)
        
        gap_comparison = {
            group: {
                "company_gap": company_gaps.get(group, 0),
                "market_gap": market_gaps.get(group, 0),
                "difference": company_gaps.get(group, 0) - market_gaps.get(group, 0)
            }
            for group in set(list(company_gaps.keys()) + list(market_gaps.keys()))
        }
        
        results["wage_gap_analysis"][attr] = {
            "gaps": gap_comparison,
            "summary": {
                "max_difference": max(abs(v["difference"]) for v in gap_comparison.values()),
                "concerning_groups": [
                    group for group, metrics in gap_comparison.items()
                    if metrics["difference"] < -0.03  # 3% threshold
                ]
            }
        }
    
    # Generate recommendations
    recommendations = []
    
    # Representation recommendations
    for attr, metrics in results["representation_metrics"].items():
        if metrics["summary"]["underrepresented_groups"]:
            recommendations.append({
                "category": "representation",
                "priority": "high",
                "attribute": attr,
                "finding": f"Underrepresentation in groups: {', '.join(metrics['summary']['underrepresented_groups'])}",
                "actions": [
                    "Review recruitment practices",
                    "Expand sourcing channels",
                    "Implement targeted outreach programs",
                    "Review job requirements for potential barriers"
                ]
            })
    
    # Wage gap recommendations
    for attr, analysis in results["wage_gap_analysis"].items():
        if analysis["summary"]["concerning_groups"]:
            recommendations.append({
                "category": "compensation",
                "priority": "high",
                "attribute": attr,
                "finding": f"Above-market wage gaps for: {', '.join(analysis['summary']['concerning_groups'])}",
                "actions": [
                    "Conduct detailed pay equity analysis",
                    "Review compensation policies",
                    "Implement structured pay bands",
                    "Establish clear promotion criteria"
                ]
            })
    
    results["recommendations"] = recommendations
    return results

def generate_fairness_documentation(
    analysis_results: Dict[str, Any],
    output_format: str = "markdown"
) -> str:
    """
    Generate comprehensive documentation of fairness analysis results.
    
    Args:
        analysis_results: Results from .fairness analysis
        output_format: Output format ("markdown" or "html")
    """
    try:
        import pdoc
        _pdoc_available = True
    except ImportError:
        _pdoc_available = False
    
    doc_sections = []
    
    # 1. Executive Summary
    summary = ["# Fairness Analysis Report", ""]
    if "summary" in analysis_results:
        summary.extend([
            "## Executive Summary",
            "",
            f"Overall Fairness Score: {analysis_results['summary'].get('overall_fairness_score', 'N/A')}",
            "",
            "### Critical Issues",
            ""
        ])
        
        for issue in analysis_results["summary"].get("critical_issues", []):
            summary.append(f"- {issue}")
        summary.append("")
    
    doc_sections.append("\n".join(summary))
    
    # 2. Detailed Analysis
    if "detailed_analysis" in analysis_results:
        detailed = ["## Detailed Analysis", ""]
        analysis = analysis_results["detailed_analysis"]
        
        # Pay Equity
        if "pay_equity" in analysis:
            detailed.extend([
                "### Pay Equity Analysis",
                "",
                f"- Largest Gap: {analysis['pay_equity'].get('largest_gap', 'N/A')}%",
                "- Statistical Significance: " + 
                ("Yes" if analysis['pay_equity'].get('statistical_significance') else "No"),
                ""
            ])
        
        # Bias Metrics
        if "bias_metrics" in analysis:
            detailed.extend(["### Bias Metrics", ""])
            for attr, metrics in analysis["bias_metrics"].items():
                detailed.extend([
                    f"#### {attr}",
                    "",
                    f"- Demographic Parity: {metrics.get('demographic_parity', 'N/A')}",
                    f"- Equalized Odds: {metrics.get('equalized_odds', 'N/A')}",
                    ""
                ])
        
        doc_sections.append("\n".join(detailed))
    
    # 3. Recommendations
    if "recommendations" in analysis_results:
        recs = ["## Recommendations", ""]
        for rec in analysis_results["recommendations"]:
            recs.extend([
                f"### {rec.get('title', 'Unnamed Recommendation')}",
                "",
                f"Priority: {rec.get('priority', 'N/A')}",
                "",
                "Actions:",
                ""
            ])
            for action in rec.get("actions", []):
                recs.append(f"- {action}")
            recs.append("")
        
        doc_sections.append("\n".join(recs))
    
    # 4. Technical Details
    if "model_performance" in analysis_results:
        tech = ["## Technical Details", ""]
        tech.extend([
            "### Model Performance",
            "",
            "```python",
            str(analysis_results["model_performance"]),
            "```",
            ""
        ])
        
        doc_sections.append("\n".join(tech))
    
    # Combine all sections
    documentation = "\n".join(doc_sections)
    
    # Convert to HTML if requested
    if output_format == "html" and _pdoc_available:
        documentation = pdoc.html.markdown2html(documentation)
    
    return documentation

def create_fairness_visualizations(
    analysis_results: Dict[str, Any],
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Create visualizations for fairness analysis results.
    
    Args:
        analysis_results: Results from .fairness analysis
        output_format: Output format ("json" for data, "html" for plotly figures)
    """
    try:
        import plotly.graph_objs as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        _plotly_available = True
    except ImportError:
        _plotly_available = False
        
    visualizations = {
        "pay_distribution": None,
        "trend_charts": None,
        "fairness_metrics": None,
        "data": {}
    }
    
    if not _plotly_available and output_format == "html":
        warnings.warn("Plotly not available. Returning JSON data only.")
        output_format = "json"
    
    # 1. Pay Distribution Analysis
    if "pay_gap" in analysis_results:
        gaps = analysis_results["pay_gap"]
        dist_data = {
            "groups": list(gaps["group_stats"].keys()),
            "means": [stats["avg_salary"] for stats in gaps["group_stats"].values()],
            "counts": [stats["count"] for stats in gaps["group_stats"].values()]
        }
        
        if output_format == "html" and _plotly_available:
            fig = go.Figure()
            for i, group in enumerate(dist_data["groups"]):
                fig.add_trace(go.Bar(
                    name=group,
                    x=[group],
                    y=[dist_data["means"][i]],
                    text=[f"n={dist_data['counts'][i]}"],
                    textposition="auto"
                ))
            fig.update_layout(
                title="Pay Distribution by Group",
                yaxis_title="Average Salary",
                showlegend=True
            )
            visualizations["pay_distribution"] = fig.to_json()
        else:
            visualizations["data"]["pay_distribution"] = dist_data
    
    # 2. Trend Analysis
    if "trends" in analysis_results and "historical_metrics" in analysis_results["trends"]:
        trends = analysis_results["trends"]["historical_metrics"]
        if output_format == "html" and _plotly_available:
            fig = make_subplots(rows=len(trends), cols=1,
                              subplot_titles=list(trends.keys()))
            for i, (metric, values) in enumerate(trends.items(), 1):
                fig.add_trace(
                    go.Scatter(x=list(range(len(values))), y=values,
                             name=metric, mode="lines+markers"),
                    row=i, col=1
                )
            fig.update_layout(height=300*len(trends), title_text="Fairness Metrics Over Time")
            visualizations["trend_charts"] = fig.to_json()
        else:
            visualizations["data"]["trends"] = trends
    
    # 3. Fairness Metrics Dashboard
    if "bias_metrics" in analysis_results:
        metrics_data = {
            attr: {
                "demographic_parity": metrics["overall"]["demographic_parity"],
                "equalized_odds": metrics["overall"]["equalized_odds"]
            }
            for attr, metrics in analysis_results["bias_metrics"].items()
        }
        
        if output_format == "html" and _plotly_available:
            # Create a heatmap of fairness metrics
            attrs = list(metrics_data.keys())
            metrics = ["demographic_parity", "equalized_odds"]
            values = [[metrics_data[attr][m] for attr in attrs] for m in metrics]
            
            fig = go.Figure(data=go.Heatmap(
                z=values,
                x=attrs,
                y=metrics,
                colorscale="RdYlGn",
                zmid=0
            ))
            fig.update_layout(title="Fairness Metrics Heatmap")
            visualizations["fairness_metrics"] = fig.to_json()
        else:
            visualizations["data"]["fairness_metrics"] = metrics_data
    
    return visualizations

def analyze_compensation_structure(
    salaries: List[float],
    features: List[List[float]],
    sensitive_attributes: Dict[str, List[str]],
    historical_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze compensation structure using machine learning techniques to identify
    potential sources of bias and unfairness.
    
    Args:
        salaries: List of salary values
        features: Job-related features (experience, skills, performance, etc.)
        sensitive_attributes: Protected attributes (gender, ethnicity, etc.)
        historical_data: Optional historical compensation data for trend analysis
    """
    features_array = np.array(features)
    salary_array = np.array(salaries)
    
    results = {}
    
    # 1. Feature importance analysis
    model = LinearRegression()
    model.fit(features_array, salary_array)
    
    # Analyze which factors contribute most to salary differences
    feature_importance = {
        f"feature_{i}": float(coef)
        for i, coef in enumerate(model.coef_)
    }
    
    results["feature_importance"] = {
        "coefficients": feature_importance,
        "explained_variance": float(r2_score(salary_array, model.predict(features_array)))
    }
    
    # 2. Counterfactual fairness analysis
    counterfactuals = {}
    for attr_name, attr_values in sensitive_attributes.items():
        # Create counterfactual predictions by neutralizing protected attribute
        unique_values = list(set(attr_values))
        cf_predictions = []
        
        for value in unique_values:
            # Create copy with this value for all instances
            cf_attrs = {
                k: v if k != attr_name else [value] * len(v)
                for k, v in sensitive_attributes.items()
            }
            
            # Get predictions
            if _fairlearn_available:
                cf_constraint = DemographicParity()
                cf_model = ExponentiatedGradient(
                    LinearRegression(),
                    constraints=cf_constraint,
                    eps=0.01
                )
                cf_model.fit(
                    features_array,
                    salary_array,
                    sensitive_features=cf_attrs[attr_name]
                )
                cf_predictions.append(cf_model.predict(features_array))
        
        if cf_predictions:
            # Calculate disparity between counterfactuals
            max_diff = float(max(np.mean(p) for p in cf_predictions) - 
                           min(np.mean(p) for p in cf_predictions))
            
            counterfactuals[attr_name] = {
                "counterfactual_disparity": max_diff,
                "interpretation": "high" if max_diff > 0.1 else "low"
            }
    
    results["counterfactual_analysis"] = counterfactuals
    
    # 3. Bias amplification analysis
    bias_amplification = {}
    for attr_name, attr_values in sensitive_attributes.items():
        # Split data by attribute
        unique_values = list(set(attr_values))
        group_means = {}
        group_stds = {}
        
        for value in unique_values:
            mask = np.array(attr_values) == value
            group_means[value] = float(np.mean(salary_array[mask]))
            group_stds[value] = float(np.std(salary_array[mask]))
        
        # Check if disparities grow with salary level
        correlation = np.corrcoef(
            salary_array,
            [group_stds[v] for v in attr_values]
        )[0, 1]
        
        bias_amplification[attr_name] = {
            "correlation": float(correlation),
            "increasing_disparity": correlation > 0.1,
            "group_means": group_means,
            "group_stds": group_stds
        }
    
    results["bias_amplification"] = bias_amplification
    
    # 4. Recommendation generation
    recommendations = []
    
    # Check feature importance
    if results["feature_importance"]["explained_variance"] < 0.7:
        recommendations.append({
            "type": "structure",
            "priority": "high",
            "message": "Compensation structure lacks clear relationship with job-related factors"
        })
    
    # Check counterfactual fairness
    high_disparity_attrs = [
        attr for attr, data in counterfactuals.items()
        if data["interpretation"] == "high"
    ]
    if high_disparity_attrs:
        recommendations.append({
            "type": "bias",
            "priority": "high",
            "message": f"High counterfactual disparity detected for: {', '.join(high_disparity_attrs)}"
        })
    
    # Check bias amplification
    increasing_bias_attrs = [
        attr for attr, data in bias_amplification.items()
        if data["increasing_disparity"]
    ]
    if increasing_bias_attrs:
        recommendations.append({
            "type": "trend",
            "priority": "medium",
            "message": f"Increasing disparities at higher salary levels for: {', '.join(increasing_bias_attrs)}"
        })
    
    results["recommendations"] = recommendations
    
    return results
