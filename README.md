# dl-md

A command-line tool for downloading and converting website content from sitemaps to markdown format with organized directory structure.

## Overview

`dl-md` extracts URLs from XML sitemaps and downloads each page as markdown, automatically organizing the content into a directory structure that mirrors the website's URL hierarchy.

## Features

- **Sitemap Processing**: Extracts URLs from XML sitemaps using trafilatura
- **Automatic Directory Structure**: Creates directories based on URL paths
- **Markdown Conversion**: Downloads and converts web pages to clean markdown format
- **Progress Reporting**: Shows real-time progress as URLs are processed
- **Dry Run Mode**: Preview what would be downloaded without actually fetching content
- **Verbose Output**: Detailed logging for troubleshooting
- **Comprehensive Testing**: Full test suite with 85% code coverage

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/donbowman/dl-md
cd dl-md
poetry install
```

### Using pip

```bash
pip install dl-md
```

## Usage

### Basic Usage

```bash
dl <sitemap-url> [<sitemap-url> ...]
```

### Example

Download all 'anyx-guide' and 'ufaq' post types from the Agilicus website:

```bash
dl https://www.agilicus.com/anyx-guide-sitemap.xml https://www.agilicus.com/ufaq-sitemap.xml
```

This command will:
1. Fetch both sitemap files from www.agilicus.com
2. Extract all URLs from both sitemaps
3. Create a directory structure like:
   ```
   agilicus.com/
   ├── anyx-guide/
   │   ├── getting-started.md
   │   ├── installation.md
   │   └── configuration.md
   └── ufaq/
       ├── troubleshooting.md
       ├── common-issues.md
       └── support.md
   ```
4. Download each URL and convert it to clean markdown format

### Command Options

- `-v, --verbose`: Enable detailed output showing progress and debugging information
- `-o, --output-dir TEXT`: Specify output directory (default: current directory)
- `--dry-run`: Show what would be downloaded without actually fetching content
- `--help`: Show help message and exit

### Examples

**Verbose output with custom directory:**
```bash
dl --verbose --output-dir ./downloads https://example.com/sitemap.xml
```

**Dry run to preview structure:**
```bash
dl --dry-run https://example.com/sitemap.xml
```

**Multiple sitemaps:**
```bash
dl https://site1.com/sitemap.xml https://site2.com/sitemap.xml
```

## Directory Structure

The tool creates directories based on URL structure:

| URL | Directory | Filename |
|-----|-----------|----------|
| `https://www.example.com/blog/post1` | `example.com/blog/` | `post1.md` |
| `https://example.com/docs/guide` | `example.com/docs/` | `guide.md` |
| `https://example.com/` | `example.com/` | `index.md` |

## How It Works

1. **Sitemap Parsing**: Uses trafilatura's `sitemap_search()` to extract URLs from XML sitemaps
2. **URL Processing**: Parses each URL to determine directory structure and filename
3. **Content Fetching**: Downloads each page using trafilatura's `fetch_url()`
4. **Markdown Conversion**: Converts HTML content to clean markdown using trafilatura's `extract()`
5. **File Organization**: Saves markdown files in organized directory structure

## Development

### Running Tests

```bash
poetry run pytest
```

### Running Tests with Coverage

```bash
poetry run pytest --cov=dl_md --cov-report=term-missing
```

### Project Structure

```
dl-md/
├── dl_md/
│   ├── __init__.py
│   └── cli.py          # Main CLI implementation
├── tests/
│   ├── __init__.py
│   └── test_cli.py     # Comprehensive test suite
├── pyproject.toml      # Project configuration
├── poetry.lock         # Dependency lock file
└── README.md           # This file
```

## Dependencies

- **click**: Command-line interface framework
- **trafilatura**: Web scraping and content extraction
- **requests**: HTTP library for web requests
- **pytest**: Testing framework (development)
- **pytest-cov**: Coverage reporting (development)

## Error Handling

The tool gracefully handles various error conditions:

- **Network errors**: Continues processing other URLs if one fails
- **Invalid sitemaps**: Reports errors and continues with other sitemaps
- **Content extraction failures**: Logs failures and continues processing
- **File system errors**: Reports permission or disk space issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `poetry run pytest`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Check the verbose output with `-v` flag for debugging information
- Review the test suite for usage examples
- Open an issue on the project repository