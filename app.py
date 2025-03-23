import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from scraper import scrape_website, validate_url

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-key")

@app.route("/", methods=["GET"])
def index():
    """Render the home page with scraping form"""
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    """Handle form submission and perform web scraping"""
    url = request.form.get("url", "").strip()
    elements = request.form.getlist("elements")
    
    # Validate URL
    if not url:
        flash("Please enter a URL", "danger")
        return redirect(url_for("index"))
    
    if not validate_url(url):
        flash("Please enter a valid URL", "danger")
        return redirect(url_for("index"))
    
    # No elements selected
    if not elements:
        flash("Please select at least one element type to scrape", "warning")
        return redirect(url_for("index"))
    
    try:
        # Perform scraping
        results = scrape_website(url, elements)
        
        # Store results in session
        session["results"] = results
        session["url"] = url
        session["elements"] = elements
        
        return redirect(url_for("results"))
    
    except Exception as e:
        app.logger.error(f"Error scraping {url}: {str(e)}")
        flash(f"Error scraping the website: {str(e)}", "danger")
        return redirect(url_for("index"))

@app.route("/results")
def results():
    """Display scraping results"""
    # Get results from session
    results = session.get("results", {})
    url = session.get("url", "")
    elements = session.get("elements", [])
    
    if not results:
        flash("No results to display. Please submit a URL to scrape.", "warning")
        return redirect(url_for("index"))
    
    return render_template("results.html", results=results, url=url, elements=elements)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template("index.html", error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template("index.html", error="Server error occurred"), 500
