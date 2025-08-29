#!/bin/bash

# CAV Studio Test Runner - Playwright Tests Only
# This script runs comprehensive Playwright tests

set -e

echo "🧪 CAV Studio Test Runner"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if servers are running
log "Checking server status..."
if ! curl -s http://localhost:8000/ > /dev/null; then
    error "Backend server not running. Start with: ./quick-setup.sh"
fi

if ! curl -s http://localhost:8080/ > /dev/null; then
    error "Frontend server not running. Start with: ./quick-setup.sh"
fi

success "Both servers are running"

# Navigate to testing directory
cd testing

log "Setting up Playwright environment..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    log "Installing Playwright dependencies..."
    npm ci
fi

# Install browsers
log "Installing Playwright browsers..."
npx playwright install --with-deps chromium

# Run comprehensive tests
echo ""
log "🚀 Running Comprehensive Test Suite"
log "===================================="

# Test 1: Image Upload and CAV Training
log "🔍 Test Suite 1: Image Upload & CAV Training"
npx playwright test test-image-upload-cav.spec.js --reporter=line || warning "Some image upload tests failed"

echo ""

# Test 2: Learn Concept Button 
log "🔍 Test Suite 2: Learn Concept Button Navigation"
npx playwright test test-learn-concept-button.spec.js --reporter=line || warning "Some Learn Concept tests failed"

echo ""

# Test 3: Complete Suite Summary
log "🔍 Test Suite 3: Complete Integration Tests"
npx playwright test --reporter=line,html || warning "Some integration tests failed"

echo ""

# Generate and display results
log "📊 Generating test reports..."

if [ -f "playwright-report/index.html" ]; then
    success "Test report generated successfully!"
    echo ""
    echo "📋 Test Results Summary:"
    echo "========================"
    echo "📄 HTML Report: testing/playwright-report/index.html"
    echo "🌐 Open in browser: file://$(pwd)/playwright-report/index.html"
    echo ""
    
    # Try to show test summary from report
    if command -v grep > /dev/null && [ -f "playwright-report/index.html" ]; then
        echo "🎯 Quick Summary:"
        if grep -q "passed" playwright-report/index.html 2>/dev/null; then
            log "✅ Tests completed - check HTML report for detailed results"
        fi
    fi
else
    warning "HTML report not generated - check test output above"
fi

echo ""
echo "🎉 Test execution completed!"
echo ""
echo "💡 Next steps:"
echo "   • Open the HTML report to see detailed results"
echo "   • Fix any failing tests and re-run"
echo "   • Use './run-automation.sh --test-only' as an alternative"