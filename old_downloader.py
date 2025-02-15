from playwright.sync_api import sync_playwright, TimeoutError
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

CDP_URL = "http://127.0.0.1:9222"
CANVAS_CHECK_URL = "https://umsystem.instructure.com/courses/"
PROGRESS_SELECTOR = "#x_of_x_students_frd" 
NEXT_BUTTON_SELECTOR = "#next-student-button" 
DOWNLOAD_BTN_SELECTOR = "a.submission-file-download.icon-download"  
STUDENT_NAME_SELECTOR = ".ui-selectmenu-item-header"

DOWNLOAD_DIR = os.path.join(script_dir, "ZombieOutbreakAssignments/downloaded")  

unsubmitted_students = []

def find_canvas_tab(pages):
    for page in pages:
        if CANVAS_CHECK_URL in page.url:
            return page
    return None

def connect_to_browser():
    """Connect to an already open Edge session via CDP."""
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp(CDP_URL)
    context = browser.contexts[0]
    page = find_canvas_tab(context.pages)
    
    if not page:
        print("Canvas tab not found.")
        browser.close()
        playwright.stop()
        exit(1)
    
    return playwright, browser, page

def get_progress(page):
    try:
        progress_text = page.query_selector(PROGRESS_SELECTOR).inner_text()
        current_page, total_pages = map(int, progress_text.split("/"))
        return current_page, total_pages
    except Exception as e:
        print(f"Error retrieving progress: {e}")
        return 0, 1  # Default to prevent infinite loop

def click_next_button(page):
    """Clicks the next arrow button to move to the next page."""
    try:
        page.click(NEXT_BUTTON_SELECTOR, timeout=5000)
    except TimeoutError:
        print("Next button not found or not clickable.")
    except Exception as e:
        print(f"Error clicking next button: {e}")

def batch_download_zip():
    """Main function to handle downloading ZIPs and navigating pages."""
    # Ensure the download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    playwright, browser, page = connect_to_browser()

    print(f"Connected to page: {page.url}")

    while True:
        current_page, total_pages = get_progress(page)
        if current_page >= total_pages:
            print("All pages processed!")
            break

        try:
            student_element = page.query_selector(STUDENT_NAME_SELECTOR)
            if not student_element:
                print("Student name element not found.")
                break
            current_student = student_element.inner_text().strip()
        except Exception as e:
            print(f"Error retrieving student name: {e}")
            current_student = "unknown_student"

        print(f"Processing {current_student}. Page {current_page} / {total_pages}...")
        
        if page.is_visible(DOWNLOAD_BTN_SELECTOR):
            try:
                with page.expect_download() as download_info:
                    print(f"Attempting to click download button: {DOWNLOAD_BTN_SELECTOR}")
                    page.click(DOWNLOAD_BTN_SELECTOR, force=True)
                
                download = download_info.value
                # Define the desired download path
                save_path = os.path.join(DOWNLOAD_DIR, f"{current_student}.zip")
                download.save_as(save_path)
                print(f"Assignment downloaded and saved to: {save_path}\n")
            except TimeoutError:
                print("Download button not found or download did not start in time.\n")
            except Exception as e:
                print(f"No assignment submitted or an error occurred: {e}\n")
        else:
            print(f"Download button not visible. No assignment submitted for {current_student} at page {current_page}.\n")
            unsubmitted_students.append(current_student)

        click_next_button(page)
        
        # Wait for the student name to change, indicating the next page has loaded
        try:
            page.wait_for_selector(STUDENT_NAME_SELECTOR, timeout=10000)  # Wait up to 10 seconds
        except TimeoutError:
            print("Next student page did not load in time.")
            break

    # Clean up
    

if __name__ == "__main__":
    batch_download_zip()