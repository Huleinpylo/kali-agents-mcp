"""
Machine Learning and Adaptation Algorithms for Kali Agents.

This module implements various ML algorithms for agent adaptation and learning:
- Fuzzy Logic for decision making under uncertainty
- Genetic Algorithms for strategy optimization
- Reinforcement Learning for behavior adaptation
- Pattern Recognition for threat intelligence
"""

import numpy as np
import random
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.models.core import LearningContext, PerformanceMetrics


class AdaptationAlgorithm(ABC):
    """Base class for all adaptation algorithms."""
    
    def __init__(self, name: str, parameters: Dict[str, Any]):
        self.name = name
        self.parameters = parameters
        self.learning_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def adapt(self, context: LearningContext, performance: PerformanceMetrics) -> Dict[str, Any]:
        """Apply the adaptation algorithm."""
        pass
    
    @abstractmethod
    def evaluate_performance(self, results: List[Dict[str, Any]]) -> float:
        """Evaluate the performance of recent adaptations."""
        pass


class FuzzyLogicEngine(AdaptationAlgorithm):
    """
    Fuzzy Logic Engine for decision making under uncertainty.
    Used for agent task assignment, resource allocation, and risk assessment.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__("fuzzy_logic", parameters)
        self.linguistic_variables = {
            "task_complexity": {
                "low": (0.0, 0.0, 0.4),
                "medium": (0.2, 0.5, 0.8),
                "high": (0.6, 1.0, 1.0)
            },
            "agent_workload": {
                "low": (0.0, 0.0, 0.3),
                "medium": (0.2, 0.5, 0.8),
                "high": (0.7, 1.0, 1.0)
            },
            "assignment_score": {
                "poor": (0.0, 0.0, 0.3),
                "fair": (0.2, 0.5, 0.8),
                "excellent": (0.7, 1.0, 1.0)
            }
        }
    
    def triangular_membership(self, x: float, params: Tuple[float, float, float]) -> float:
        """Calculate triangular membership function value."""
        a, b, c = params
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        else:
            return (c - x) / (c - b)
    
    def make_decision(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """Make a fuzzy logic decision."""
        # Simplified fuzzy inference
        complexity = inputs.get("task_complexity", 0.5)
        workload = inputs.get("agent_workload", 0.5)
        
        # Simple rule: if complexity is low and workload is low, score is excellent
        if complexity < 0.4 and workload < 0.3:
            score = 0.9
        elif complexity > 0.6 or workload > 0.7:
            score = 0.2
        else:
            score = 0.5
        
        return {
            "decision": {"assignment_score": score},
            "confidence": 0.8
        }
    
    def adapt(self, context: LearningContext, performance: PerformanceMetrics) -> Dict[str, Any]:
        """Apply fuzzy logic adaptation."""
        return {
            "algorithm": "fuzzy_logic",
            "adjustments": {"rules_updated": True},
            "confidence": performance.confidence_score
        }
    
    def evaluate_performance(self, results: List[Dict[str, Any]]) -> float:
        """Evaluate fuzzy logic performance."""
        if not results:
            return 0.5
        return sum(r.get("assignment_score", 0.5) for r in results) / len(results)


@dataclass
class Individual:
    """Individual in genetic algorithm population."""
    genes: List[float]
    fitness: float = 0.0
    
    def mutate(self, mutation_rate: float):
        """Apply mutation."""
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] += random.gauss(0, 0.1)
                self.genes[i] = max(0.0, min(1.0, self.genes[i]))


class GeneticAlgorithm(AdaptationAlgorithm):
    """
    Genetic Algorithm for strategy optimization.
    Used for optimizing agent strategies and parameter tuning.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__("genetic_algorithm", parameters)
        self.population_size = parameters.get("population_size", 20)
        self.mutation_rate = parameters.get("mutation_rate", 0.1)
        self.gene_count = parameters.get("gene_count", 5)
        self.population: List[Individual] = []
        self.generation = 0
    
    def initialize_population(self):
        """Initialize random population."""
        self.population = []
        for _ in range(self.population_size):
            genes = [random.random() for _ in range(self.gene_count)]
            self.population.append(Individual(genes))
    
    def fitness_function(self, individual: Individual, context: Dict[str, Any]) -> float:
        """Calculate fitness of an individual."""
        genes = individual.genes
        
        # Simple fitness: balance between speed and accuracy
        speed_gene = genes[0] if len(genes) > 0 else 0.5
        accuracy_gene = genes[1] if len(genes) > 1 else 0.5
        
        fitness = (speed_gene + accuracy_gene) / 2.0
        return fitness
    
    def evolve_generation(self, context: Dict[str, Any]):
        """Evolve one generation."""
        if not self.population:
            self.initialize_population()
        
        # Calculate fitness
        for individual in self.population:
            individual.fitness = self.fitness_function(individual, context)
        
        # Sort by fitness
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Keep best half, create new half
        survivors = self.population[:self.population_size // 2]
        new_population = survivors.copy()
        
        # Create offspring
        while len(new_population) < self.population_size:
            parent = random.choice(survivors)
            child = Individual(parent.genes.copy())
            child.mutate(self.mutation_rate)
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1
    
    def adapt(self, context: LearningContext, performance: PerformanceMetrics) -> Dict[str, Any]:
        """Apply genetic algorithm adaptation."""
        fitness_context = {
            "success_rate": performance.success_rate,
            "execution_time": performance.execution_time
        }
        
        # Evolve for a few generations
        for _ in range(5):
            self.evolve_generation(fitness_context)
        
        best_individual = max(self.population, key=lambda x: x.fitness)
        
        return {
            "algorithm": "genetic_algorithm",
            "best_strategy": best_individual.genes,
            "fitness": best_individual.fitness,
            "generation": self.generation
        }
    
    def evaluate_performance(self, results: List[Dict[str, Any]]) -> float:
        """Evaluate genetic algorithm performance."""
        if not results:
            return 0.0
        fitness_values = [r.get("fitness", 0.0) for r in results]
        return max(fitness_values) if fitness_values else 0.0


class QLearningAgent(AdaptationAlgorithm):
    """
    Q-Learning for agent behavior adaptation.
    Used for learning optimal action sequences.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__("q_learning", parameters)
        self.learning_rate = parameters.get("learning_rate", 0.1)
        self.discount_factor = parameters.get("discount_factor", 0.9)
        self.epsilon = parameters.get("epsilon", 0.1)
        self.q_table: Dict[str, Dict[str, float]] = {}
        self.reward_history: List[float] = []
    
    def get_q_value(self, state: str, action: str) -> float:
        """Get Q-value for state-action pair."""
        if state not in self.q_table:
            self.q_table[state] = {}
        return self.q_table[state].get(action, 0.0)
    
    def choose_action(self, state: str, possible_actions: List[str]) -> str:
        """Choose action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.choice(possible_actions)
        else:
            q_values = {action: self.get_q_value(state, action) for action in possible_actions}
            return max(q_values, key=q_values.get)
    
    def learn_from_experience(self, state: str, action: str, reward: float, next_state: str):
        """Learn from experience."""
        if state not in self.q_table:
            self.q_table[state] = {}
        
        current_q = self.get_q_value(state, action)
        max_next_q = max(self.q_table.get(next_state, {}).values(), default=0.0)
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
        
        self.reward_history.append(reward)
    
    def adapt(self, context: LearningContext, performance: PerformanceMetrics) -> Dict[str, Any]:
        """Apply Q-learning adaptation."""
        reward = performance.success_rate - 0.5  # Convert to reward signal
        self.reward_history.append(reward)
        
        # Adjust exploration based on performance
        if performance.success_rate < 0.6:
            self.epsilon = min(0.3, self.epsilon * 1.1)
        else:
            self.epsilon = max(0.01, self.epsilon * 0.9)
        
        return {
            "algorithm": "q_learning",
            "q_table_size": len(self.q_table),
            "epsilon": self.epsilon,
            "average_reward": np.mean(self.reward_history[-10:]) if self.reward_history else 0.0
        }
    
    def evaluate_performance(self, results: List[Dict[str, Any]]) -> float:
        """Evaluate Q-learning performance."""
        if not results:
            return 0.0
        rewards = [r.get("average_reward", 0.0) for r in results]
        return np.mean(rewards) if rewards else 0.0


class PatternRecognition:
    """Pattern Recognition for threat intelligence and attack pattern detection."""
    
    def __init__(self):
        self.known_patterns: Dict[str, Dict[str, Any]] = {}
        self.pattern_frequency: Dict[str, int] = {}
        self.pattern_success_rate: Dict[str, float] = {}
    
    def add_pattern(self, pattern_id: str, pattern_data: Dict[str, Any], success: bool = True):
        """Add a new pattern to the knowledge base."""
        self.known_patterns[pattern_id] = pattern_data
        self.pattern_frequency[pattern_id] = self.pattern_frequency.get(pattern_id, 0) + 1
        
        if pattern_id in self.pattern_success_rate:
            current_rate = self.pattern_success_rate[pattern_id]
            count = self.pattern_frequency[pattern_id]
            new_rate = (current_rate * (count - 1) + (1.0 if success else 0.0)) / count
            self.pattern_success_rate[pattern_id] = new_rate
        else:
            self.pattern_success_rate[pattern_id] = 1.0 if success else 0.0
    
    def recognize_pattern(self, data: Dict[str, Any], similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Recognize patterns in given data."""
        matches = []
        
        for pattern_id, pattern_data in self.known_patterns.items():
            similarity = self._calculate_similarity(data, pattern_data)
            
            if similarity >= similarity_threshold:
                matches.append({
                    "pattern_id": pattern_id,
                    "similarity": similarity,
                    "frequency": self.pattern_frequency[pattern_id],
                    "success_rate": self.pattern_success_rate[pattern_id]
                })
        
        matches.sort(key=lambda x: x["similarity"] * x["success_rate"], reverse=True)
        return matches
    
    def _calculate_similarity(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> float:
        """Calculate similarity between two data patterns."""
        if not data1 or not data2:
            return 0.0
        
        common_keys = set(data1.keys()) & set(data2.keys())
        if not common_keys:
            return 0.0
        
        similarity_scores = []
        for key in common_keys:
            val1, val2 = data1[key], data2[key]
            if isinstance(val1, str) and isinstance(val2, str):
                if val1.lower() == val2.lower():
                    similarity_scores.append(1.0)
                else:
                    similarity_scores.append(0.0)
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                max_val = max(abs(val1), abs(val2), 1)
                diff = abs(val1 - val2)
                similarity_scores.append(max(0.0, 1.0 - diff / max_val))
        
        return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0


def create_adaptation_algorithm(algorithm_type: str, parameters: Dict[str, Any]) -> AdaptationAlgorithm:
    """Factory function to create adaptation algorithms."""
    if algorithm_type == "fuzzy_logic":
        return FuzzyLogicEngine(parameters)
    elif algorithm_type == "genetic_algorithm":
        return GeneticAlgorithm(parameters)
    elif algorithm_type == "q_learning":
        return QLearningAgent(parameters)
    else:
        raise ValueError(f"Unknown algorithm type: {algorithm_type}")
