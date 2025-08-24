#!/usr/bin/env python3
"""
Unit tests for the dl-md CLI functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from dl_md.cli import main, create_directory_structure, download_url_as_markdown, extract_urls_from_sitemap


class TestCreateDirectoryStructure:
    """Test the create_directory_structure function."""
    
    def test_simple_url_with_filename(self):
        """Test URL with simple path and filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            url = "https://www.example.com/blog/post1"
            directory_path, filename = create_directory_structure(url, temp_dir)
            
            expected_dir = Path(temp_dir) / "example.com" / "blog"
            assert directory_path == str(expected_dir)
            assert filename == "post1"
            assert expected_dir.exists()
    
    def test_url_without_www(self):
        """Test URL without www prefix."""
        with tempfile.TemporaryDirectory() as temp_dir:
            url = "https://example.com/docs/guide"
            directory_path, filename = create_directory_structure(url, temp_dir)
            
            expected_dir = Path(temp_dir) / "example.com" / "docs"
            assert directory_path == str(expected_dir)
            assert filename == "guide"
            assert expected_dir.exists()
    
    def test_url_with_deep_path(self):
        """Test URL with multiple path segments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            url = "https://www.agilicus.com/faq/troubleshooting/network"
            directory_path, filename = create_directory_structure(url, temp_dir)
            
            expected_dir = Path(temp_dir) / "agilicus.com" / "faq" / "troubleshooting"
            assert directory_path == str(expected_dir)
            assert filename == "network"
            assert expected_dir.exists()
    
    def test_url_with_root_path_only(self):
        """Test URL with only root path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            url = "https://example.com/"
            directory_path, filename = create_directory_structure(url, temp_dir)
            
            expected_dir = Path(temp_dir) / "example.com"
            assert directory_path == str(expected_dir)
            assert filename == "index"
            assert expected_dir.exists()
    
    def test_url_without_path(self):
        """Test URL without any path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            url = "https://example.com"
            directory_path, filename = create_directory_structure(url, temp_dir)
            
            expected_dir = Path(temp_dir) / "example.com"
            assert directory_path == str(expected_dir)
            assert filename == "index"
            assert expected_dir.exists()


class TestDownloadUrlAsMarkdown:
    """Test the download_url_as_markdown function."""
    
    @patch('dl_md.cli.fetch_url')
    @patch('dl_md.cli.extract')
    def test_successful_download(self, mock_extract, mock_fetch_url):
        """Test successful URL download and markdown extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the trafilatura functions
            mock_fetch_url.return_value = "<html><body>Test content</body></html>"
            mock_extract.return_value = "# Test Content\n\nThis is test content."
            
            url = "https://example.com/test"
            result = download_url_as_markdown(url, temp_dir, "test", verbose=False)
            
            assert result is True
            
            # Check that file was created
            file_path = Path(temp_dir) / "test.md"
            assert file_path.exists()
            
            # Check file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == "# Test Content\n\nThis is test content."
            
            # Verify mocks were called
            mock_fetch_url.assert_called_once_with(url)
            mock_extract.assert_called_once_with("<html><body>Test content</body></html>", output_format='markdown')
    
    @patch('dl_md.cli.fetch_url')
    def test_failed_fetch(self, mock_fetch_url):
        """Test handling of failed URL fetch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_fetch_url.return_value = None
            
            url = "https://example.com/nonexistent"
            result = download_url_as_markdown(url, temp_dir, "test", verbose=False)
            
            assert result is False
            
            # Check that no file was created
            file_path = Path(temp_dir) / "test.md"
            assert not file_path.exists()
    
    @patch('dl_md.cli.fetch_url')
    @patch('dl_md.cli.extract')
    def test_failed_extraction(self, mock_extract, mock_fetch_url):
        """Test handling of failed content extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_fetch_url.return_value = "<html><body>Test content</body></html>"
            mock_extract.return_value = None
            
            url = "https://example.com/test"
            result = download_url_as_markdown(url, temp_dir, "test", verbose=False)
            
            assert result is False
            
            # Check that no file was created
            file_path = Path(temp_dir) / "test.md"
            assert not file_path.exists()


class TestExtractUrlsFromSitemap:
    """Test the extract_urls_from_sitemap function."""
    
    @patch('dl_md.cli.sitemap_search')
    def test_successful_sitemap_extraction(self, mock_sitemap_search):
        """Test successful sitemap URL extraction."""
        mock_sitemap_search.return_value = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/blog/post1"
        ]
        
        sitemap_url = "https://example.com/sitemap.xml"
        result = extract_urls_from_sitemap(sitemap_url, verbose=False)
        
        expected_urls = {
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/blog/post1"
        }
        assert result == expected_urls
        mock_sitemap_search.assert_called_once_with(sitemap_url)
    
    @patch('dl_md.cli.sitemap_search')
    def test_empty_sitemap(self, mock_sitemap_search):
        """Test handling of empty sitemap."""
        mock_sitemap_search.return_value = []
        
        sitemap_url = "https://example.com/sitemap.xml"
        result = extract_urls_from_sitemap(sitemap_url, verbose=False)
        
        assert result == set()
    
    @patch('dl_md.cli.sitemap_search')
    def test_sitemap_extraction_error(self, mock_sitemap_search):
        """Test handling of sitemap extraction error."""
        mock_sitemap_search.side_effect = Exception("Network error")
        
        sitemap_url = "https://example.com/sitemap.xml"
        result = extract_urls_from_sitemap(sitemap_url, verbose=False)
        
        assert result == set()


class TestCLIIntegration:
    """Test the CLI integration."""
    
    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Extract URLs from sitemaps" in result.output
        assert "SITEMAP_URLS" in result.output
    
    def test_cli_no_arguments(self):
        """Test CLI with no arguments."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        
        assert result.exit_code == 2
        assert "Missing argument" in result.output
    
    @patch('dl_md.cli.extract_urls_from_sitemap')
    def test_cli_dry_run(self, mock_extract_urls):
        """Test CLI dry run functionality."""
        mock_extract_urls.return_value = {
            "https://example.com/page1",
            "https://example.com/page2"
        }
        
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(main, [
                '--dry-run',
                '--verbose',
                '--output-dir', temp_dir,
                'https://example.com/sitemap.xml'
            ])
            
            assert result.exit_code == 0
            assert "DRY RUN" in result.output
            assert "Found 2 unique URLs" in result.output
            assert "Would process these URLs:" in result.output
    
    @patch('dl_md.cli.extract_urls_from_sitemap')
    @patch('dl_md.cli.download_url_as_markdown')
    def test_cli_full_run(self, mock_download, mock_extract_urls):
        """Test CLI full run functionality."""
        mock_extract_urls.return_value = {
            "https://example.com/page1",
            "https://example.com/page2"
        }
        mock_download.return_value = True
        
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(main, [
                '--verbose',
                '--output-dir', temp_dir,
                'https://example.com/sitemap.xml'
            ])
            
            assert result.exit_code == 0
            assert "Found 2 unique URLs to process" in result.output
            assert "Successfully processed: 2" in result.output
            assert "Failed: 0" in result.output
            
            # Verify download was called for each URL
            assert mock_download.call_count == 2


if __name__ == '__main__':
    pytest.main([__file__])