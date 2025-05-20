from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from datetime import date
from app.models.questionnaire import Questionnaire
import logging

logger = logging.getLogger(__name__)

# Definir grupos y subgrupos de gastos
EXPENSE_GROUPS = {
    "Vitales": {
        "Vivienda": ["Arriendo"],
        "Servicios": ["Servicios", "Comunicación"],
        "Alimentación": ["Mercado"],
        "Transporte": ["Transporte"],
        "Salud": ["Salud"],
        "Seguros": ["Seguros"]
    },
    "Ocio": {
        "Salidas": ["Salidas", "Domicilio"],
        "Entretenimiento": ["Antojos", "Suscripciones"],
        "Hobbies": ["Hobbies"]
    },
    "Financieros": {
        "Ahorros": ["Ahorros"],
        "Deudas": ["Deudas"],
        "Educación": ["Educación"]
    }
}

# Definir presupuestos con criterios de alineación
BUDGETS = {
    "50/30/20": {"Vitales": 50, "Ocio": 30, "Financieros": 20, "Complejidad": "Baja", "Deudas_Prioridad": "Media", "Ahorros_Prioridad": "Media"},
    "70/20/10": {"Vitales": 70, "Ocio": 20, "Financieros": 10, "Complejidad": "Baja", "Deudas_Prioridad": "Baja", "Ahorros_Prioridad": "Media"},
    "80/20": {"Vitales": 80, "Ocio": 20, "Financieros": 20, "Complejidad": "Muy Baja", "Deudas_Prioridad": "Baja", "Ahorros_Prioridad": "Baja"},
    "60/20/20": {"Vitales": 60, "Ocio": 20, "Financieros": 20, "Complejidad": "Media", "Deudas_Prioridad": "Media", "Ahorros_Prioridad": "Media"},
    "30/30/20/20": {"Vitales": 30, "Ocio": 20, "Financieros": 20, "Complejidad": "Media", "Deudas_Prioridad": "Media", "Ahorros_Prioridad": "Media"},
    "Basado en Cero": {"Vitales": 0, "Ocio": 0, "Financieros": 0, "Complejidad": "Alta", "Deudas_Prioridad": "Alta", "Ahorros_Prioridad": "Alta"},
    "Sobres": {"Vitales": 0, "Ocio": 0, "Financieros": 0, "Complejidad": "Media", "Deudas_Prioridad": "Media", "Ahorros_Prioridad": "Media"},
    "50/15/35": {"Vitales": 50, "Ocio": 15, "Financieros": 35, "Complejidad": "Media", "Deudas_Prioridad": "Media", "Ahorros_Prioridad": "Alta"},
    "10/10/80": {"Vitales": 10, "Ocio": 10, "Financieros": 80, "Complejidad": "Baja", "Deudas_Prioridad": "Baja", "Ahorros_Prioridad": "Alta"},
    "Personalizado": {"Vitales": 0, "Ocio": 0, "Financieros": 0, "Complejidad": "Alta", "Deudas_Prioridad": "Alta", "Ahorros_Prioridad": "Alta"}
}

class BudgetRecommender(ABC):
    @abstractmethod
    def recommend(self, questionnaire: Questionnaire) -> Tuple[str, Dict[str, float]]:
        """Genera una recomendación de presupuesto basada en el cuestionario."""
        pass

class WeightedScoringRecommender(BudgetRecommender):
    def __init__(self):
        self.weights = {
            "Gastos": 0.5,  # Aumentado para reflejar la importancia de los porcentajes
            "Deudas": 0.25,
            "Ahorros": 0.15,
            "Ingresos": 0.1
        }

    def calculate_expense_percentages(self, monthly_report: Optional[Dict]) -> Dict[str, float]:
        """Calcula los porcentajes de gasto por grupo (Vitales, Ocio, Financieros) desde monthly_report."""
        if not monthly_report or not monthly_report.get("entries"):
            return {"Vitales": 0, "Ocio": 0, "Financieros": 0}
        
        group_totals = {"Vitales": 0, "Ocio": 0, "Financieros": 0}
        total_expenses = monthly_report.get("total", 0)
        
        if total_expenses == 0:
            return {"Vitales": 0, "Ocio": 0, "Financieros": 0}
        
        for entry in monthly_report["entries"]:
            category = entry.get("category")
            amount = entry.get("amount", 0)
            for group, subgroups in EXPENSE_GROUPS.items():
                for subgroup, items in subgroups.items():
                    if category in items:
                        group_totals[group] += amount
                        break
        
        return {
            group: (amount / total_expenses * 100) if total_expenses > 0 else 0
            for group, amount in group_totals.items()
        }

    def count_category_groups(self, categories: List[str]) -> Dict[str, int]:
        """Cuenta cuántas categorías pertenecen a cada grupo (Vitales, Ocio, Financieros)."""
        counts = {"Vitales": 0, "Ocio": 0, "Financieros": 0}
        for category in categories:
            for group, subgroups in EXPENSE_GROUPS.items():
                for subgroup, items in subgroups.items():
                    if category in items:
                        counts[group] += 1
        return counts

    def score_budget(self, budget: Dict, expense_percentages: Dict[str, float], category_counts: Dict[str, int], has_debt: str, savings_interest: str, income: float) -> float:
        """Asigna una puntuación al presupuesto basado en alineación con criterios."""
        total_categories = sum(category_counts.values()) or 1
        category_scores = {
            "Vitales": (category_counts["Vitales"] / total_categories * 100) if budget["Vitales"] > 0 else 0,
            "Ocio": (category_counts["Ocio"] / total_categories * 100) if budget["Ocio"] > 0 else 0,
            "Financieros": (category_counts["Financieros"] / total_categories * 100) if budget["Financieros"] > 0 else 0
        }
        
        # Usar porcentajes de monthly_report si están disponibles, sino usar category_scores
        if expense_percentages["Vitales"] > 0 or expense_percentages["Ocio"] > 0 or expense_percentages["Financieros"] > 0:
            vitales_diff = abs(expense_percentages["Vitales"] - budget["Vitales"])
            ocio_diff = abs(expense_percentages["Ocio"] - budget["Ocio"])
            financieros_diff = abs(expense_percentages["Financieros"] - budget["Financieros"])
        else:
            vitales_diff = abs(category_scores["Vitales"] - budget["Vitales"])
            ocio_diff = abs(category_scores["Ocio"] - budget["Ocio"])
            financieros_diff = abs(category_scores["Financieros"] - budget["Financieros"])
        
        vitales_score = 100 - vitales_diff * 2
        ocio_score = 100 - ocio_diff * 2
        financieros_score = 100 - financieros_diff * 2
        
        debt_score = 100
        if has_debt.lower() == "yes":
            if budget["Deudas_Prioridad"] == "Alta":
                debt_score = 100
            elif budget["Deudas_Prioridad"] == "Media":
                debt_score = 70
            else:
                debt_score = 30
        else:
            if budget["Deudas_Prioridad"] == "Baja":
                debt_score = 100
            elif budget["Deudas_Prioridad"] == "Media":
                debt_score = 70
            else:
                debt_score = 50
        
        savings_score = 100
        if savings_interest.lower() == "yes":
            if budget["Ahorros_Prioridad"] == "Alta":
                savings_score = 100
            elif budget["Ahorros_Prioridad"] == "Media":
                savings_score = 70
            else:
                savings_score = 30
        elif savings_interest.lower() == "maybe":
            if budget["Ahorros_Prioridad"] == "Media":
                savings_score = 100
            elif budget["Ahorros_Prioridad"] == "Alta":
                savings_score = 70
            else:
                savings_score = 50
        else:
            if budget["Ahorros_Prioridad"] == "Baja":
                savings_score = 100
            elif budget["Ahorros_Prioridad"] == "Media":
                savings_score = 70
            else:
                savings_score = 50
        
        income_score = 100
        if income < 500000:
            if budget["Complejidad"] in ["Baja", "Muy Baja"]:
                income_score = 100
            elif budget["Complejidad"] == "Media":
                income_score = 70
            else:
                income_score = 30
        elif income < 2000000:
            if budget["Complejidad"] in ["Baja", "Media"]:
                income_score = 100
            elif budget["Complejidad"] == "Alta":
                income_score = 70
            else:
                income_score = 50
        else:
            if budget["Complejidad"] in ["Media", "Alta"]:
                income_score = 100
            elif budget["Complejidad"] == "Baja":
                income_score = 70
            else:
                income_score = 50
        
        total_score = (
            self.weights["Gastos"] * (vitales_score + ocio_score + financieros_score) / 3 +
            self.weights["Deudas"] * debt_score +
            self.weights["Ahorros"] * savings_score +
            self.weights["Ingresos"] * income_score
        ) / sum(self.weights.values())
        
        return total_score

    def generate_distribution(self, budget_name: str, income: float) -> Dict[str, float]:
        """Genera la distribución de ingresos según el presupuesto seleccionado."""
        distribution = {}
        if budget_name in ["50/30/20", "60/20/20", "50/15/35"]:
            percentages = budget_name.split("/")
            distribution = {
                "Necesidades": income * int(percentages[0]) / 100,
                "Deseos": income * int(percentages[1]) / 100,
                "Ahorros/Deudas": income * int(percentages[2]) / 100
            }
        elif budget_name == "70/20/10":
            distribution = {
                "Gastos de vida": income * 0.7,
                "Ahorros": income * 0.2,
                "Deudas/Donaciones": income * 0.1
            }
        elif budget_name == "80/20":
            distribution = {
                "Gastos totales": income * 0.8,
                "Ahorros/Deudas": income * 0.2
            }
        elif budget_name == "30/30/20/20":
            distribution = {
                "Vivienda": income * 0.3,
                "Necesidades básicas": income * 0.3,
                "Deseos": income * 0.2,
                "Ahorros/Deudas": income * 0.2
            }
        elif budget_name in ["Basado en Cero", "Personalizado"]:
            distribution = {"Asignación Manual": income}
        elif budget_name == "Sobres":
            distribution = {"Sobres Personalizados": income}
        elif budget_name == "10/10/80":
            distribution = {
                "Ahorros": income * 0.1,
                "Deudas/Donaciones": income * 0.1,
                "Gastos": income * 0.8
            }
        return distribution

    def recommend(self, questionnaire: Questionnaire) -> Tuple[str, Dict[str, float]]:
        """Genera una recomendación de presupuesto basada en el cuestionario."""
        try:
            income = float(questionnaire.ans2.get("exact_amount", 0))
            categories = questionnaire.ans3.get("gastos", [])
            has_debt = questionnaire.ans4.get("answer", "no")
            savings_interest = questionnaire.ans4.get("savings_interest", "maybe")
            monthly_report = questionnaire.monthly_report
            
            if not income:
                raise ValueError("El ingreso mensual debe ser mayor que 0")
            if not categories:
                raise ValueError("La lista de categorías no puede estar vacía")
            
            expense_percentages = self.calculate_expense_percentages(monthly_report)
            category_counts = self.count_category_groups(categories)
            
            best_budget = None
            best_score = -1
            
            for budget_name, budget in BUDGETS.items():
                score = self.score_budget(budget, expense_percentages, category_counts, has_debt, savings_interest, income)
                if score > best_score:
                    best_score = score
                    best_budget = budget_name
            
            distribution = self.generate_distribution(best_budget, income)
            
            logger.info(f"Recomendación generada: {best_budget} para usuario {questionnaire.user_id}")
            return best_budget, distribution
        except Exception as e:
            logger.error(f"Error al generar recomendación: {str(e)}")
            raise ValueError(f"Error al generar recomendación: {str(e)}")