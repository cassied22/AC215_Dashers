from unittest.mock import patch, MagicMock
import sys
sys.path.append('/app')
from model_training import gemini_fine_tuning 

def test_gemini_fine_tuning():
    mock_project = "test-project"
    mock_location = "us-central1"
    mock_train_dataset = "gs://test-bucket/train-data"
    mock_validation_dataset = "gs://test-bucket/validation-data"
    mock_tuned_model_display_name = "tuned-gemini-model"
    mock_source_model = "gemini-1.5-flash-002"
    mock_epochs = 4
    mock_adapter_size = 4
    mock_learning_rate_multiplier = 0.9

    # Mocking the Vertex AI methods and objects
    mock_sft = MagicMock()
    mock_sft_tuning_job = MagicMock()
    mock_sft_tuning_job.has_ended = False
    mock_sft_tuning_job.tuned_model_endpoint_name = "endpoint-123"
    mock_sft_tuning_job.tuned_model_name = "model-123"

    def mock_refresh():
        mock_sft_tuning_job.has_ended = True

    mock_sft_tuning_job.refresh.side_effect = mock_refresh
    mock_sft.train.return_value = mock_sft_tuning_job

    with patch("model_training.vertexai.init") as mock_vertexai_init:
        with patch("model_training.sft", mock_sft):
            with patch("model_training.time.sleep", return_value=None):
                model_name, endpoint_name = gemini_fine_tuning(
                    project=mock_project,
                    location=mock_location,
                    train_dataset=mock_train_dataset,
                    validation_dataset=mock_validation_dataset,
                    tuned_model_display_name=mock_tuned_model_display_name,
                    source_model=mock_source_model,
                    epochs=mock_epochs,
                    adapter_size=mock_adapter_size,
                    learning_rate_multiplier=mock_learning_rate_multiplier,
                )

    # Assert vertexai.init was called correctly
    mock_vertexai_init.assert_called_once_with(project=mock_project, location=mock_location)

    # Assert sft.train was called with correct parameters
    mock_sft.train.assert_called_once_with(
        source_model=mock_source_model,
        train_dataset=mock_train_dataset,
        validation_dataset=mock_validation_dataset,
        epochs=mock_epochs,
        adapter_size=mock_adapter_size,
        learning_rate_multiplier=mock_learning_rate_multiplier,
        tuned_model_display_name=mock_tuned_model_display_name,
    )

    # Assert the final outputs are correct
    assert model_name == "model-123"
    assert endpoint_name == "endpoint-123"
