from dataset_generation.dataset_generator import ExperimentCondition

# Test configuration
TEST_CONFIG = {
    "samples_per_option": 2,  # Reduced number for testing
    "conditions": [ExperimentCondition.BASELINE],  # Example: test only baseline condition
    # Set to None to test all conditions
    # conditions=None  
}
