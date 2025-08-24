#!/usr/bin/env python3
"""
CLI entry point for dl-md package.
Downloads and processes sitemap URLs, extracting content as markdown.
"""

from pathlib import Path
from urllib.parse import urlparse

import click
from trafilatura import extract, fetch_url
from trafilatura.sitemaps import sitemap_search


def create_directory_structure(url, base_dir="."):
    """
    Create directory structure based on URL path.

    Args:
        url (str): The URL to create directories for
        base_dir (str): Base directory to create structure in

    Returns:
        tuple: (directory_path, filename) where directory_path is the created
               directory and filename is the trailing element
    """
    parsed = urlparse(url)

    # Get the domain (without www. prefix for cleaner structure)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]

    # Get the path components, excluding empty strings
    path_parts = [part for part in parsed.path.split("/") if part]

    if not path_parts:
        # If no path, use index as filename
        filename = "index"
        directory_path = Path(base_dir) / domain
    else:
        # Last part becomes the filename, rest become directories
        filename = path_parts[-1]
        directory_parts = [domain] + path_parts[:-1]
        directory_path = Path(base_dir) / Path(*directory_parts)

    # Create the directory structure
    directory_path.mkdir(parents=True, exist_ok=True)

    return str(directory_path), filename


def download_url_as_markdown(url, directory_path, filename, verbose=False):
    """
    Download a URL and save it as markdown.

    Args:
        url (str): The URL to download
        directory_path (str): Directory to save the file in
        filename (str): Base filename (without extension)
        verbose (bool): Whether to show verbose output

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if verbose:
            click.echo(f"  Fetching: {url}")

        # Fetch the URL content
        downloaded = fetch_url(url)
        if not downloaded:
            if verbose:
                click.echo(f"  Failed to fetch: {url}")
            return False

        # Extract markdown content
        markdown_content = extract(downloaded, output_format="markdown")
        if not markdown_content:
            if verbose:
                click.echo(f"  No content extracted from: {url}")
            return False

        # Save to file
        file_path = Path(directory_path) / f"{filename}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        if verbose:
            click.echo(f"  Saved: {file_path}")

        return True

    except Exception as e:
        if verbose:
            click.echo(f"  Error processing {url}: {str(e)}")
        return False


def extract_urls_from_sitemap(sitemap_url, verbose=False):
    """
    Extract URLs from a sitemap using trafilatura.

    Args:
        sitemap_url (str): The sitemap URL to process
        verbose (bool): Whether to show verbose output

    Returns:
        set: A set of unique URLs found in the sitemap
    """
    try:
        if verbose:
            click.echo(f"  Fetching sitemap: {sitemap_url}")

        # Use trafilatura's sitemap_search to extract URLs
        urls = sitemap_search(sitemap_url)

        if verbose:
            click.echo(f"  Found {len(urls) if urls else 0} URLs in sitemap")

        return set(urls) if urls else set()

    except Exception as e:
        click.echo(f"  Error processing sitemap {sitemap_url}: {str(e)}", err=True)
        return set()


@click.command()
@click.argument("sitemap_urls", nargs=-1, required=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--output-dir", "-o", default=".", help="Output directory for downloaded files"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without actually downloading",
)
def main(sitemap_urls, verbose, output_dir, dry_run):
    """
    Extract URLs from sitemaps and download each as markdown with organized
    directory structure.

    For each URL found:
    - Creates directory structure based on URL path (e.g., www.example.com/blog/)
    - Downloads the URL content as markdown
    - Saves as filename.md in the appropriate directory

    SITEMAP_URLS: One or more sitemap URLs to process
    """
    if verbose:
        click.echo(f"Processing {len(sitemap_urls)} sitemap URL(s)")
        click.echo(f"Output directory: {output_dir}")
        if dry_run:
            click.echo("DRY RUN - No files will be downloaded")

    # Set to store all unique URLs
    all_urls = set()

    # Extract URLs from all sitemaps
    for i, sitemap_url in enumerate(sitemap_urls, 1):
        if verbose:
            click.echo(f"\n[{i}/{len(sitemap_urls)}] Processing sitemap: {sitemap_url}")

        # Extract URLs from this sitemap
        urls = extract_urls_from_sitemap(sitemap_url, verbose)

        # Add to our master set (automatically handles uniqueness)
        all_urls.update(urls)

        if verbose:
            click.echo(f"  Total unique URLs so far: {len(all_urls)}")

    # Convert to sorted list for consistent processing
    unique_urls = sorted(list(all_urls))

    if not unique_urls:
        click.echo("No URLs found in any sitemap.")
        return

    click.echo(f"\nFound {len(unique_urls)} unique URLs to process")

    if dry_run:
        click.echo("\nDRY RUN - Would process these URLs:")
        for url in unique_urls:
            directory_path, filename = create_directory_structure(url, output_dir)
            click.echo(f"  {url} -> {directory_path}/{filename}.md")
        return

    # Process each URL
    successful = 0
    failed = 0

    for i, url in enumerate(unique_urls, 1):
        click.echo(f"[{i}/{len(unique_urls)}] Processing: {url}")

        # Create directory structure
        directory_path, filename = create_directory_structure(url, output_dir)

        # Download and save as markdown
        if download_url_as_markdown(url, directory_path, filename, verbose):
            successful += 1
        else:
            failed += 1
            click.echo(f"  Failed to process: {url}")

    # Summary
    click.echo("\nProcessing complete!")
    click.echo(f"Successfully processed: {successful}")
    click.echo(f"Failed: {failed}")
    click.echo(f"Total: {len(unique_urls)}")


if __name__ == "__main__":
    main()
