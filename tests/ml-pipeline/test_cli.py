import argparse
from unittest.mock import patch, MagicMock
import sys
sys.path.append('/app')
from cli import main, run_pipeline, generate_uuid 

def test_generate_uuid():
    uuid = generate_uuid(8)
    assert len(uuid) == 8
    assert all(c.isalnum() for c in uuid)

@patch("cli.data_clean")
@patch("cli.data_prepare")
@patch("cli.data_upload")
@patch("cli.gemini_fine_tuning")
@patch("cli.evaluate")
def test_run_pipeline(mock_evaluate, mock_gemini_fine_tuning, mock_data_upload, mock_data_prepare, mock_data_clean):
    mock_gemini_fine_tuning.return_value = ("mock-model", "mock-endpoint")
    mock_evaluate.return_value = 95.0

    run_pipeline()

    # Assert data processing steps were called
    mock_data_clean.assert_called_once()
    mock_data_prepare.assert_called_once()
    mock_data_upload.assert_called_once()

    # Assert model training was called with the correct parameters
    mock_gemini_fine_tuning.assert_called_once()

    # Assert model evaluation was called
    mock_evaluate.assert_called_once_with(endpoint="mock-endpoint")

@patch("cli.run_pipeline")
def test_main_pipeline(mock_run_pipeline):
    with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(pipeline=True, data_processor=False, model_training=False, model_evaluation=False)):
        main()
        mock_run_pipeline.assert_called_once()

@patch("cli.data_clean")
@patch("cli.data_prepare")
@patch("cli.data_upload")
def test_main_data_processor(mock_data_upload, mock_data_prepare, mock_data_clean):
    with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(pipeline=False, data_processor=True, model_training=False, model_evaluation=False)):
        main()
        mock_data_clean.assert_called_once()
        mock_data_prepare.assert_called_once()
        mock_data_upload.assert_called_once()

@patch("cli.gemini_fine_tuning")
def test_main_model_training(mock_gemini_fine_tuning):
    with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(pipeline=False, data_processor=False, model_training=True, model_evaluation=False)):
        main()
        mock_gemini_fine_tuning.assert_called_once()

@patch("cli.evaluate")
def test_main_model_evaluation(mock_evaluate):
    with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(pipeline=False, data_processor=False, model_training=False, model_evaluation=True)):
        main()
        mock_evaluate.assert_called_once()

@patch("cli.run_pipeline")
def test_main_no_args(mock_run_pipeline):
    with patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(pipeline=False, data_processor=False, model_training=False, model_evaluation=False)):
        main()
        mock_run_pipeline.assert_not_called()
