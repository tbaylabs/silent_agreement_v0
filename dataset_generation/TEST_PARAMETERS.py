from dataset_generation.chat_message_builder import ExperimentCondition

# Test configuration
TEST_CONFIG = {
    "samples_per_option": 2,  # Reduced number for testing
    "conditions": [ExperimentCondition.CONTROL_SUPPRESS_COT],  # Example: test only control condition
    # Set to None to test all conditions
    # conditions=None  
}
