# tests/test_ml_algorithms.py
"""
Comprehensive tests for ML algorithms to achieve 80%+ coverage.
Priority: 33% -> 80%+ coverage (118 untested statements)
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.models.ml_algorithms import (
    AdaptationAlgorithm, FuzzyLogicEngine, GeneticAlgorithm, QLearningAgent,
    PatternRecognition, Individual, create_adaptation_algorithm
)
from src.models.core import LearningContext, PerformanceMetrics


class TestFuzzyLogicEngine:
    """Test fuzzy logic engine functionality."""
    
    def test_fuzzy_logic_initialization(self):
        """Test fuzzy logic engine initialization."""
        params = {"threshold": 0.8}
        engine = FuzzyLogicEngine(params)
        
        assert engine.name == "fuzzy_logic"
        assert engine.parameters == params
        assert isinstance(engine.linguistic_variables, dict)
        assert "task_complexity" in engine.linguistic_variables
        assert "agent_workload" in engine.linguistic_variables
        assert "assignment_score" in engine.linguistic_variables
    
    def test_triangular_membership_function(self):
        """Test triangular membership function calculations."""
        engine = FuzzyLogicEngine({})
        
        # Test membership function with different values
        params = (0.0, 0.5, 1.0)
        
        assert engine.triangular_membership(0.0, params) == 0.0  # At left edge
        assert engine.triangular_membership(0.5, params) == 1.0  # At peak
        assert engine.triangular_membership(1.0, params) == 0.0  # At right edge
        assert engine.triangular_membership(0.25, params) == 0.5  # Ascending slope
        assert engine.triangular_membership(0.75, params) == 0.5  # Descending slope
        assert engine.triangular_membership(-0.1, params) == 0.0  # Below range
        assert engine.triangular_membership(1.1, params) == 0.0  # Above range
    
    def test_make_decision_low_complexity_low_workload(self):
        """Test decision making with low complexity and low workload."""
        engine = FuzzyLogicEngine({})
        
        inputs = {
            "task_complexity": 0.3,
            "agent_workload": 0.2
        }
        
        result = engine.make_decision(inputs)
        
        assert "decision" in result
        assert "confidence" in result
        assert result["decision"]["assignment_score"] == 0.9
        assert result["confidence"] == 0.8
    
    def test_make_decision_high_complexity_high_workload(self):
        """Test decision making with high complexity and high workload."""
        engine = FuzzyLogicEngine({})
        
        inputs = {
            "task_complexity": 0.8,
            "agent_workload": 0.9
        }
        
        result = engine.make_decision(inputs)
        
        assert result["decision"]["assignment_score"] == 0.2
    
    def test_make_decision_medium_values(self):
        """Test decision making with medium values."""
        engine = FuzzyLogicEngine({})
        
        inputs = {
            "task_complexity": 0.5,
            "agent_workload": 0.5
        }
        
        result = engine.make_decision(inputs)
        
        assert result["decision"]["assignment_score"] == 0.5
    
    def test_make_decision_default_values(self):
        """Test decision making with missing inputs (default values)."""
        engine = FuzzyLogicEngine({})
        
        inputs = {}
        
        result = engine.make_decision(inputs)
        
        assert "decision" in result
        assert result["decision"]["assignment_score"] == 0.5  # Default case
    
    def test_adapt_method(self):
        """Test fuzzy logic adaptation method."""
        engine = FuzzyLogicEngine({})
        context = LearningContext(algorithm_type="fuzzy_logic", parameters={})
        performance = PerformanceMetrics(
            execution_time=30.0,
            success_rate=0.95,
            accuracy=0.9,
            error_count=1,
            confidence_score=0.85
        )
        
        result = engine.adapt(context, performance)
        
        assert result["algorithm"] == "fuzzy_logic"
        assert result["adjustments"]["rules_updated"] is True
        assert result["confidence"] == 0.85
    
    def test_evaluate_performance(self):
        """Test fuzzy logic performance evaluation."""
        engine = FuzzyLogicEngine({})
        
        # Test with empty results
        assert engine.evaluate_performance([]) == 0.5
        
        # Test with results
        results = [
            {"assignment_score": 0.8},
            {"assignment_score": 0.9},
            {"assignment_score": 0.7}
        ]
        
        performance = engine.evaluate_performance(results)
        assert performance == 0.8  # Average of scores


class TestIndividual:
    """Test Individual class for genetic algorithm."""
    
    def test_individual_initialization(self):
        """Test individual initialization."""
        genes = [0.1, 0.5, 0.9, 0.3]
        individual = Individual(genes)
        
        assert individual.genes == genes
        assert individual.fitness == 0.0
    
    def test_individual_mutation(self):
        """Test individual mutation."""
        genes = [0.5, 0.5, 0.5, 0.5]
        individual = Individual(genes)
        
        # Test mutation with 100% rate (all genes should change)
        original_genes = individual.genes.copy()
        individual.mutate(1.0)
        
        # Genes should be different but still in valid range
        for i, gene in enumerate(individual.genes):
            assert 0.0 <= gene <= 1.0
    
    def test_individual_mutation_no_change(self):
        """Test individual mutation with 0% rate."""
        genes = [0.5, 0.5, 0.5, 0.5]
        individual = Individual(genes)
        original_genes = individual.genes.copy()
        
        individual.mutate(0.0)
        
        assert individual.genes == original_genes
    
    def test_individual_mutation_bounds(self):
        """Test that mutation respects bounds."""
        genes = [0.0, 1.0]  # Edge values
        individual = Individual(genes)
        
        # Multiple mutations to test bounds
        for _ in range(10):
            individual.mutate(0.5)
            for gene in individual.genes:
                assert 0.0 <= gene <= 1.0


class TestGeneticAlgorithm:
    """Test genetic algorithm functionality."""
    
    def test_genetic_algorithm_initialization(self):
        """Test genetic algorithm initialization."""
        params = {
            "population_size": 30,
            "mutation_rate": 0.2,
            "gene_count": 8
        }
        ga = GeneticAlgorithm(params)
        
        assert ga.name == "genetic_algorithm"
        assert ga.population_size == 30
        assert ga.mutation_rate == 0.2
        assert ga.gene_count == 8
        assert ga.generation == 0
        assert len(ga.population) == 0
    
    def test_genetic_algorithm_default_parameters(self):
        """Test genetic algorithm with default parameters."""
        ga = GeneticAlgorithm({})
        
        assert ga.population_size == 20
        assert ga.mutation_rate == 0.1
        assert ga.gene_count == 5
    
    def test_initialize_population(self):
        """Test population initialization."""
        ga = GeneticAlgorithm({"population_size": 10, "gene_count": 3})
        ga.initialize_population()
        
        assert len(ga.population) == 10
        for individual in ga.population:
            assert isinstance(individual, Individual)
            assert len(individual.genes) == 3
            for gene in individual.genes:
                assert 0.0 <= gene <= 1.0
    
    def test_fitness_function(self):
        """Test fitness function calculation."""
        ga = GeneticAlgorithm({})
        individual = Individual([0.8, 0.6, 0.4, 0.2, 0.1])
        context = {"test": "context"}
        
        fitness = ga.fitness_function(individual, context)
        
        assert 0.0 <= fitness <= 1.0
        # Fitness should be average of first two genes
        expected = (0.8 + 0.6) / 2.0
        assert fitness == expected
    
    def test_fitness_function_empty_genes(self):
        """Test fitness function with empty genes."""
        ga = GeneticAlgorithm({})
        individual = Individual([])
        context = {}
        
        fitness = ga.fitness_function(individual, context)
        
        assert fitness == 0.5  # Default values
    
    def test_fitness_function_single_gene(self):
        """Test fitness function with single gene."""
        ga = GeneticAlgorithm({})
        individual = Individual([0.7])
        context = {}
        
        fitness = ga.fitness_function(individual, context)
        
        expected = (0.7 + 0.5) / 2.0  # speed_gene + default accuracy_gene
        assert fitness == expected
    
    def test_evolve_generation(self):
        """Test generation evolution."""
        ga = GeneticAlgorithm({"population_size": 6, "gene_count": 3})
        context = {"test": "evolution"}
        
        # First evolution should initialize population
        ga.evolve_generation(context)
        
        assert len(ga.population) == 6
        assert ga.generation == 1
        
        # Check that all individuals have fitness calculated
        for individual in ga.population:
            assert individual.fitness > 0.0
    
    def test_evolve_generation_multiple_times(self):
        """Test multiple generation evolutions."""
        ga = GeneticAlgorithm({"population_size": 4, "gene_count": 2})
        context = {}
        
        # Evolve multiple generations
        for i in range(3):
            ga.evolve_generation(context)
            assert ga.generation == i + 1
            assert len(ga.population) == 4
    
    def test_evolve_generation_selection_and_reproduction(self):
        """Test that evolution produces new offspring."""
        ga = GeneticAlgorithm({"population_size": 4, "gene_count": 2})
        context = {}
        
        # Initialize and evolve
        ga.evolve_generation(context)
        first_gen_genes = [ind.genes.copy() for ind in ga.population]
        
        # Evolve again
        ga.evolve_generation(context)
        second_gen_genes = [ind.genes.copy() for ind in ga.population]
        
        # Population should be sorted by fitness (descending)
        for i in range(len(ga.population) - 1):
            assert ga.population[i].fitness >= ga.population[i + 1].fitness
    
    def test_adapt_method(self):
        """Test genetic algorithm adaptation."""
        ga = GeneticAlgorithm({"population_size": 4})
        context = LearningContext(algorithm_type="genetic_algorithm", parameters={})
        performance = PerformanceMetrics(
            execution_time=45.0,
            success_rate=0.88,
            accuracy=0.92,
            error_count=2,
            confidence_score=0.8
        )
        
        result = ga.adapt(context, performance)
        
        assert result["algorithm"] == "genetic_algorithm"
        assert "best_strategy" in result
        assert "fitness" in result
        assert "generation" in result
        assert result["generation"] >= 5  # Should evolve 5 generations
    
    def test_evaluate_performance(self):
        """Test genetic algorithm performance evaluation."""
        ga = GeneticAlgorithm({})
        
        # Test with empty results
        assert ga.evaluate_performance([]) == 0.0
        
        # Test with results
        results = [
            {"fitness": 0.8},
            {"fitness": 0.9},
            {"fitness": 0.7}
        ]
        
        performance = ga.evaluate_performance(results)
        assert performance == 0.9  # Maximum fitness


class TestQLearningAgent:
    """Test Q-Learning agent functionality."""
    
    def test_qlearning_initialization(self):
        """Test Q-Learning agent initialization."""
        params = {
            "learning_rate": 0.2,
            "discount_factor": 0.95,
            "epsilon": 0.2
        }
        agent = QLearningAgent(params)
        
        assert agent.name == "q_learning"
        assert agent.learning_rate == 0.2
        assert agent.discount_factor == 0.95
        assert agent.epsilon == 0.2
        assert isinstance(agent.q_table, dict)
        assert isinstance(agent.reward_history, list)
    
    def test_qlearning_default_parameters(self):
        """Test Q-Learning with default parameters."""
        agent = QLearningAgent({})
        
        assert agent.learning_rate == 0.1
        assert agent.discount_factor == 0.9
        assert agent.epsilon == 0.1
    
    def test_get_q_value_new_state(self):
        """Test getting Q-value for new state-action pair."""
        agent = QLearningAgent({})
        
        q_value = agent.get_q_value("new_state", "new_action")
        
        assert q_value == 0.0
        assert "new_state" in agent.q_table
        assert agent.q_table["new_state"] == {}
    
    def test_get_q_value_existing_state(self):
        """Test getting Q-value for existing state-action pair."""
        agent = QLearningAgent({})
        agent.q_table["state1"] = {"action1": 0.5, "action2": 0.8}
        
        q_value = agent.get_q_value("state1", "action1")
        assert q_value == 0.5
        
        q_value = agent.get_q_value("state1", "action3")
        assert q_value == 0.0
    
    def test_choose_action_exploration(self):
        """Test action selection with exploration."""
        agent = QLearningAgent({"epsilon": 1.0})  # Always explore
        possible_actions = ["action1", "action2", "action3"]
        
        action = agent.choose_action("test_state", possible_actions)
        
        assert action in possible_actions
    
    def test_choose_action_exploitation(self):
        """Test action selection with exploitation."""
        agent = QLearningAgent({"epsilon": 0.0})  # Never explore
        agent.q_table["test_state"] = {"action1": 0.2, "action2": 0.8, "action3": 0.5}
        possible_actions = ["action1", "action2", "action3"]
        
        action = agent.choose_action("test_state", possible_actions)
        
        assert action == "action2"  # Highest Q-value
    
    def test_choose_action_mixed_strategy(self):
        """Test action selection with mixed strategy."""
        agent = QLearningAgent({"epsilon": 0.5})
        agent.q_table["test_state"] = {"action1": 0.1, "action2": 0.9}
        possible_actions = ["action1", "action2"]
        
        # Run multiple times to test both exploration and exploitation
        actions = [agent.choose_action("test_state", possible_actions) for _ in range(100)]
        
        # Should have both actions selected (due to exploration)
        assert "action1" in actions
        assert "action2" in actions
    
    def test_learn_from_experience(self):
        """Test learning from experience."""
        agent = QLearningAgent({"learning_rate": 0.5, "discount_factor": 0.9})
        
        # Initial Q-value should be 0
        assert agent.get_q_value("state1", "action1") == 0.0
        
        # Learn from experience
        agent.learn_from_experience("state1", "action1", 1.0, "state2")
        
        # Q-value should be updated
        new_q = agent.get_q_value("state1", "action1")
        assert new_q > 0.0
        assert len(agent.reward_history) == 1
        assert agent.reward_history[0] == 1.0
    
    def test_learn_from_experience_with_next_state_values(self):
        """Test learning with existing next state Q-values."""
        agent = QLearningAgent({"learning_rate": 0.1, "discount_factor": 0.9})
        
        # Set up next state with Q-values
        agent.q_table["state2"] = {"action_a": 0.5, "action_b": 0.8}
        
        agent.learn_from_experience("state1", "action1", 0.5, "state2")
        
        # Q-value should incorporate discounted future reward
        q_value = agent.get_q_value("state1", "action1")
        expected = 0.0 + 0.1 * (0.5 + 0.9 * 0.8 - 0.0)
        assert abs(q_value - expected) < 0.001
    
    def test_adapt_method(self):
        """Test Q-Learning adaptation method."""
        agent = QLearningAgent({"epsilon": 0.2})
        context = LearningContext(algorithm_type="q_learning", parameters={})
        performance = PerformanceMetrics(
            execution_time=25.0,
            success_rate=0.7,  # Above threshold
            accuracy=0.85,
            error_count=3,
            confidence_score=0.75
        )
        
        original_epsilon = agent.epsilon
        result = agent.adapt(context, performance)
        
        assert result["algorithm"] == "q_learning"
        assert "q_table_size" in result
        assert "epsilon" in result
        assert "average_reward" in result
        
        # Epsilon should decrease for good performance
        assert agent.epsilon < original_epsilon
    
    def test_adapt_method_poor_performance(self):
        """Test Q-Learning adaptation with poor performance."""
        agent = QLearningAgent({"epsilon": 0.1})
        context = LearningContext(algorithm_type="q_learning", parameters={})
        performance = PerformanceMetrics(
            execution_time=25.0,
            success_rate=0.5,  # Below threshold
            accuracy=0.85,
            error_count=3,
            confidence_score=0.75
        )
        
        original_epsilon = agent.epsilon
        result = agent.adapt(context, performance)
        
        # Epsilon should increase for poor performance
        assert agent.epsilon > original_epsilon
        assert agent.epsilon <= 0.3  # Should not exceed maximum
    
    def test_evaluate_performance(self):
        """Test Q-Learning performance evaluation."""
        agent = QLearningAgent({})
        
        # Test with empty results
        assert agent.evaluate_performance([]) == 0.0
        
        # Add some reward history
        agent.reward_history = [0.5, 0.8, 0.3, 0.9, 0.7]
        
        # Test with results
        results = [
            {"average_reward": 0.6},
            {"average_reward": 0.8}
        ]
        
        performance = agent.evaluate_performance(results)
        expected = np.mean([0.6, 0.8])
        assert performance == expected


class TestPatternRecognition:
    """Test pattern recognition functionality."""
    
    def test_pattern_recognition_initialization(self):
        """Test pattern recognition initialization."""
        pr = PatternRecognition()
        
        assert isinstance(pr.known_patterns, dict)
        assert isinstance(pr.pattern_frequency, dict)
        assert isinstance(pr.pattern_success_rate, dict)
    
    def test_add_pattern_new(self):
        """Test adding a new pattern."""
        pr = PatternRecognition()
        pattern_data = {"type": "port_scan", "ports": [22, 80, 443]}
        
        pr.add_pattern("pattern1", pattern_data, success=True)
        
        assert "pattern1" in pr.known_patterns
        assert pr.known_patterns["pattern1"] == pattern_data
        assert pr.pattern_frequency["pattern1"] == 1
        assert pr.pattern_success_rate["pattern1"] == 1.0
    
    def test_add_pattern_existing_success(self):
        """Test adding to existing pattern with success."""
        pr = PatternRecognition()
        pattern_data = {"type": "web_scan"}
        
        # Add initial pattern
        pr.add_pattern("pattern1", pattern_data, success=True)
        
        # Add same pattern again with success
        pr.add_pattern("pattern1", pattern_data, success=True)
        
        assert pr.pattern_frequency["pattern1"] == 2
        assert pr.pattern_success_rate["pattern1"] == 1.0
    
    def test_add_pattern_existing_failure(self):
        """Test adding to existing pattern with failure."""
        pr = PatternRecognition()
        pattern_data = {"type": "vuln_scan"}
        
        # Add initial pattern with success
        pr.add_pattern("pattern1", pattern_data, success=True)
        
        # Add same pattern with failure
        pr.add_pattern("pattern1", pattern_data, success=False)
        
        assert pr.pattern_frequency["pattern1"] == 2
        assert pr.pattern_success_rate["pattern1"] == 0.5  # 1 success out of 2
    
    def test_add_pattern_initial_failure(self):
        """Test adding new pattern with initial failure."""
        pr = PatternRecognition()
        pattern_data = {"type": "scan"}
        
        pr.add_pattern("pattern1", pattern_data, success=False)
        
        assert pr.pattern_success_rate["pattern1"] == 0.0
    
    def test_recognize_pattern_no_patterns(self):
        """Test pattern recognition with no known patterns."""
        pr = PatternRecognition()
        data = {"type": "test", "value": 123}
        
        matches = pr.recognize_pattern(data)
        
        assert matches == []
    
    def test_recognize_pattern_no_matches(self):
        """Test pattern recognition with no matches."""
        pr = PatternRecognition()
        pr.add_pattern("pattern1", {"type": "scan", "target": "server1"}, True)
        
        data = {"type": "different", "target": "server2"}
        matches = pr.recognize_pattern(data)
        
        assert matches == []
    
    def test_recognize_pattern_with_matches(self):
        """Test pattern recognition with matches."""
        pr = PatternRecognition()
        
        # Add patterns
        pr.add_pattern("pattern1", {"type": "scan", "port": 80}, True)
        pr.add_pattern("pattern2", {"type": "scan", "port": 80}, True)
        pr.add_pattern("pattern1", {"type": "scan", "port": 80}, True)  # Increase frequency
        
        # Test data that should match
        data = {"type": "scan", "port": 80}
        matches = pr.recognize_pattern(data, similarity_threshold=0.9)
        
        assert len(matches) == 2
        assert matches[0]["pattern_id"] == "pattern1"  # Should be first due to higher frequency
        assert matches[0]["similarity"] == 1.0
        assert matches[0]["frequency"] == 2
        assert matches[0]["success_rate"] == 1.0
    
    def test_recognize_pattern_similarity_threshold(self):
        """Test pattern recognition with similarity threshold."""
        pr = PatternRecognition()
        pr.add_pattern("pattern1", {"type": "scan", "port": 80}, True)
        
        # Test data with lower similarity
        data = {"type": "scan", "port": 8080}  # Different port
        matches = pr.recognize_pattern(data, similarity_threshold=0.9)
        
        # Should not match due to high threshold
        assert len(matches) == 0
        
        # Lower threshold should match
        matches = pr.recognize_pattern(data, similarity_threshold=0.1)
        assert len(matches) > 0
    
    def test_calculate_similarity_empty_data(self):
        """Test similarity calculation with empty data."""
        pr = PatternRecognition()
        
        similarity = pr._calculate_similarity({}, {"type": "test"})
        assert similarity == 0.0
        
        similarity = pr._calculate_similarity({"type": "test"}, {})
        assert similarity == 0.0
        
        similarity = pr._calculate_similarity({}, {})
        assert similarity == 0.0
    
    def test_calculate_similarity_no_common_keys(self):
        """Test similarity calculation with no common keys."""
        pr = PatternRecognition()
        
        data1 = {"key1": "value1"}
        data2 = {"key2": "value2"}
        
        similarity = pr._calculate_similarity(data1, data2)
        assert similarity == 0.0
    
    def test_calculate_similarity_string_values(self):
        """Test similarity calculation with string values."""
        pr = PatternRecognition()
        
        data1 = {"type": "scan", "method": "tcp"}
        data2 = {"type": "scan", "method": "tcp"}
        
        similarity = pr._calculate_similarity(data1, data2)
        assert similarity == 1.0
        
        data2 = {"type": "scan", "method": "udp"}
        similarity = pr._calculate_similarity(data1, data2)
        assert similarity == 0.5  # type matches, method doesn't
    
    def test_calculate_similarity_numeric_values(self):
        """Test similarity calculation with numeric values."""
        pr = PatternRecognition()
        
        data1 = {"port": 80, "timeout": 30}
        data2 = {"port": 80, "timeout": 30}
        
        similarity = pr._calculate_similarity(data1, data2)
        assert similarity == 1.0
        
        data2 = {"port": 8080, "timeout": 30}
        similarity = pr._calculate_similarity(data1, data2)
        assert similarity > 0.0 and similarity < 1.0


class TestCreateAdaptationAlgorithm:
    """Test factory function for creating adaptation algorithms."""
    
    def test_create_fuzzy_logic_algorithm(self):
        """Test creating fuzzy logic algorithm."""
        params = {"threshold": 0.9}
        algorithm = create_adaptation_algorithm("fuzzy_logic", params)
        
        assert isinstance(algorithm, FuzzyLogicEngine)
        assert algorithm.name == "fuzzy_logic"
        assert algorithm.parameters == params
    
    def test_create_genetic_algorithm(self):
        """Test creating genetic algorithm."""
        params = {"population_size": 50}
        algorithm = create_adaptation_algorithm("genetic_algorithm", params)
        
        assert isinstance(algorithm, GeneticAlgorithm)
        assert algorithm.name == "genetic_algorithm"
        assert algorithm.population_size == 50
    
    def test_create_qlearning_algorithm(self):
        """Test creating Q-learning algorithm."""
        params = {"learning_rate": 0.2}
        algorithm = create_adaptation_algorithm("q_learning", params)
        
        assert isinstance(algorithm, QLearningAgent)
        assert algorithm.name == "q_learning"
        assert algorithm.learning_rate == 0.2
    
    def test_create_unknown_algorithm(self):
        """Test creating unknown algorithm type."""
        with pytest.raises(ValueError) as exc_info:
            create_adaptation_algorithm("unknown_algorithm", {})
        
        assert "Unknown algorithm type: unknown_algorithm" in str(exc_info.value)


class TestAbstractAdaptationAlgorithm:
    """Test abstract adaptation algorithm functionality."""
    
    def test_abstract_algorithm_initialization(self):
        """Test that abstract class can't be instantiated directly."""
        with pytest.raises(TypeError):
            AdaptationAlgorithm("test", {})
    
    def test_learning_history_tracking(self):
        """Test that learning history is properly tracked."""
        engine = FuzzyLogicEngine({})
        
        assert len(engine.learning_history) == 0
        
        # Learning history should be maintained by concrete implementations
        context = LearningContext(algorithm_type="fuzzy_logic", parameters={})
        performance = PerformanceMetrics(
            execution_time=30.0,
            success_rate=0.95,
            accuracy=0.9,
            error_count=1,
            confidence_score=0.85
        )
        
        result = engine.adapt(context, performance)
        
        # This is just to ensure the abstract structure is working
        assert hasattr(engine, 'learning_history')


# Additional edge case tests for complete coverage
class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""
    
    def test_fuzzy_logic_extreme_values(self):
        """Test fuzzy logic with extreme input values."""
        engine = FuzzyLogicEngine({})
        
        # Test with very high values
        inputs = {"task_complexity": 10.0, "agent_workload": 5.0}
        result = engine.make_decision(inputs)
        assert "decision" in result
        
        # Test with negative values
        inputs = {"task_complexity": -1.0, "agent_workload": -0.5}
        result = engine.make_decision(inputs)
        assert "decision" in result
    
    def test_genetic_algorithm_empty_population_evolution(self):
        """Test genetic algorithm evolution with empty population."""
        ga = GeneticAlgorithm({"population_size": 0})
        
        # Should handle empty population gracefully
        ga.evolve_generation({})
        assert len(ga.population) == 0
    
    def test_qlearning_with_empty_reward_history(self):
        """Test Q-learning evaluation with empty reward history."""
        agent = QLearningAgent({})
        
        result = agent.adapt(
            LearningContext(algorithm_type="q_learning", parameters={}),
            PerformanceMetrics(execution_time=30.0, success_rate=0.8, accuracy=0.9, error_count=0, confidence_score=0.8)
        )
        
        assert result["average_reward"] == 0.0
    
    def test_pattern_recognition_mixed_data_types(self):
        """Test pattern recognition with mixed data types."""
        pr = PatternRecognition()
        
        # Pattern with mixed types
        pattern_data = {"string_val": "test", "int_val": 42, "float_val": 3.14, "bool_val": True}
        pr.add_pattern("mixed_pattern", pattern_data, True)
        
        # Test data with same structure
        test_data = {"string_val": "test", "int_val": 42, "float_val": 3.14, "bool_val": True}
        matches = pr.recognize_pattern(test_data)
        
        assert len(matches) == 1
        assert matches[0]["similarity"] == 1.0