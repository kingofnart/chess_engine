import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # set up chromedriver
    chrome_driver_path=ChromeDriverManager().install()
    print(f"executable_path: {chrome_driver_path}")
    if "THIRD_PARTY_NOTICES" in chrome_driver_path:
        print("THIRD_PARTY_NOTICES in path, setting path manually to use 126.0.6478.182")
        chrome_driver_path = "/root/.wdm/drivers/chromedriver/linux64/126.0.6478.182/chromedriver-linux64/chromedriver"
    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Wait for the app to be ready before calling register_testuser
    for attempt in range(10):
        try:
            print(f"Attempting to load login page... Attempt {attempt+1}")
            app_url = os.getenv("APP_URL", "http://localhost:8000")
            print(f"os.getenv: {app_url}")
            driver.get(app_url)
            if driver.title: 
                print(f"App is ready, title: {driver.title}")
                break
            else:
                print("Attempt failed, retrying...")
        except Exception as e:
            print(f"Try failed on attempt {attempt+1} exception: {e}")
            time.sleep(3)

    register_testuser(driver)
    driver.get(os.getenv("APP_URL", "http://localhost:8000"))

    yield driver
    driver.quit()

def test_valid_login(driver):
    print("---------- test_valid_login ----------")
    try:
        login(driver)
    except TimeoutException as e:
        print(f"TimeoutException: {e}")
        screenshot_path = "/static/screenshots/login_timeout.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        raise
    assert "Chess Game" in driver.title


def test_invalid_login(driver):
    print("---------- test_invalid_login ----------")
    driver.get("http://localhost:8000/login")
    print(f"Current URL: {driver.current_url}")
    username_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')
    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    
    username_input.send_keys("invalid_username")
    password_input.send_keys("invalid_password")
    login_button.click()
    
    error_message = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'error')))
    assert "Invalid credentials" in error_message.text


def test_navigation_to_register(driver):
    print("---------- test_navigation_to_register ----------")
    driver.get("http://localhost:8000/login")
    register_link = driver.find_element(By.CSS_SELECTOR, 'a[href="/register"]')
    register_link.click()
    
    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:8000/register"))
    assert "Register" in driver.title


def test_navigation_to_login(driver):
    print("---------- test_navigation_to_login ----------")
    driver.get("http://localhost:8000/register")
    login_link = driver.find_element(By.CSS_SELECTOR, 'a[href="/login"]')
    login_link.click()
    
    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:8000/login"))
    assert "Login" in driver.title


def test_logout(driver):
    print("---------- test_logout ----------")
    login(driver)
    logout_button = driver.find_element(By.ID, 'logout')
    logout_button.click()
    
    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:8000/login"))
    assert "Login" in driver.title



def test_invalid_moves(driver):
    print("---------- test_invalid_moves ----------")
    login(driver)
    moves = [("1,4", "4,4"), ("6,4", "3,4"), ("0,3", "5,3"), ("7,7", "5,7"), ("0,2", "3,5"), ("1,4", "2,3")]
    
    start(driver)
    apply_moves(driver, moves)
    input_coords = reset_coords()
    input_names = reset_names()

    check_board_images(driver, input_coords, input_names)
    resign(driver)
    reset(driver) 


def test_simple_moves(driver):
    print("---------- test_simple_moves ----------")
    login(driver)
    moves = [("1,4", "3,4"), ("6,4", "4,4"), ("0,6", "2,5"), ("7,1", "5,2")]
    
    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()
    
    input_coords[0][5] = ("2,5")
    input_coords[0][12] = ("3,4")
    input_coords[1][4] = ("5,2")
    input_coords[1][12] = ("4,4")
    
    check_board_images(driver, input_coords, input_names)
    resign(driver)
    reset(driver)


def test_threefold(driver):
    print("---------- test_threefold ----------")
    login(driver)
    moves = [("1,4", "2,4"), ("6,4", "5,4"), ("0,4", "1,4"), ("7,4", "6,4"), ("1,4", "0,4"),
             ("6,4", "7,4"), ("0,4", "1,4"), ("7,4", "6,4"), ("1,4", "0,4"), ("6,4", "7,4")]

    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()

    input_coords[0][12] = ("2,4")
    input_coords[1][12] = ("5,4")
    
    check_board_images(driver, input_coords, input_names)
    reset(driver)


def test_special_moves(driver):
    print("---------- test_special_moves ----------")
    login(driver)
    moves = [("1,7", "3,7"), ("6,3", "4,3"), ("3,7", "4,7"), ("6,6", "4,6"), ("4,7", "5,6"),
             ("6,4", "5,4"), ("5,6", "6,7"), ("6,2", "5,2"), ("6,7", "7,6"), ("7,5", "5,3")]
    
    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()
    
    input_names[0][15] = "Q"
    input_coords[0][15] = ("7,6")
    input_coords[1][5] = ("-1,-1")
    input_coords[1][10] = ("5,2")
    input_coords[1][11] = ("4,3")
    input_coords[1][12] = ("5,4")
    input_coords[1][14] = ("-1,-1")
    input_coords[1][15] = ("-1,-1")
    
    check_board_images(driver, input_coords, input_names)
    resign(driver)
    reset(driver)


def test_stalemate(driver):
    print("---------- test_stalemate ----------")
    login(driver)
    moves = [("1,4", "2,4"), ("6,0", "4,0"), ("0,3", "4,7"), ("7,0", "5,0"), ("4,7", "4,0"),
             ("6,7", "4,7"), ("4,0", "6,2"), ("5,0", "5,7"), ("1,7", "3,7"), ("6,5", "5,5"),
             ("6,2", "6,3"), ("7,4", "6,5"), ("6,3", "6,1"), ("7,3", "2,3"), ("6,1", "7,1"),
             ("2,3", "6,7"), ("7,1", "7,2"), ("6,5", "5,6"), ("7,2", "5,4")]

    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()
    
    input_coords[0][1] = ("5,4")
    input_coords[0][12] = ("2,4")
    input_coords[0][15] = ("3,7")
    input_coords[1][0] = ("5,6")
    input_coords[1][1] = ("6,7")
    input_coords[1][2] = ("5,7")
    input_coords[1][4] = ("-1,-1")
    input_coords[1][6] = ("-1,-1")
    input_coords[1][8] = ("-1,-1")
    input_coords[1][9] = ("-1,-1")
    input_coords[1][10] = ("-1,-1")
    input_coords[1][11] = ("-1,-1")
    input_coords[1][13] = ("5,5")
    input_coords[1][15] = ("4,7")
    
    check_board_images(driver, input_coords, input_names)
    reset(driver)


def test_fried_liver(driver):
    print("---------- test_fried_liver ----------")
    login(driver)
    moves = [("1,4", "3,4"), ("6,4", "4,4"), ("0,6", "2,5"), ("7,1", "5,2"), ("0,5", "3,2"), 
             ("7,6", "5,5"), ("2,5", "4,6"), ("6,3", "4,3"), ("3,4", "4,3"), ("5,5", "4,3"),
             ("4,6", "6,5"), ("7,4", "6,5"), ("0,3", "2,5"), ("6,5", "7,6"), ("3,2", "4,3"),
             ("7,3", "4,3"), ("2,5", "4,3"), ("7,2", "5,4"), ("4,3", "5,4")]
    
    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()
    
    input_coords[0][1] = ("5,4")
    input_coords[0][5] = ("-1,-1")
    input_coords[0][7] = ("-1,-1")
    input_coords[0][12] = ("-1,-1")
    input_coords[1][0] = ("7,6")
    input_coords[1][4] = ("5,2")
    input_coords[1][12] = ("4,4")
    input_coords[1][1] = ("-1,-1")
    input_coords[1][6] = ("-1,-1")
    input_coords[1][11] = ("-1,-1")
    input_coords[1][13] = ("-1,-1")
    
    check_board_images(driver, input_coords, input_names)
    reset(driver)


def test_opera(driver):
    print("---------- test_opera ----------")
    login(driver)
    moves = [("1,4", "3,4"), ("6,4", "4,4"), ("0,6", "2,5"), ("6,3", "5,3"), ("1,3", "3,3"), 
             ("7,2", "3,6"), ("3,3", "4,4"), ("3,6", "2,5"), ("0,3", "2,5"), ("5,3", "4,4"),
             ("0,5", "3,2"), ("7,6", "5,5"), ("2,5", "2,1"), ("7,3", "6,4"), ("0,1", "2,2"), 
             ("6,2", "5,2"), ("0,2", "4,6"), ("6,1", "4,1"), ("2,2", "4,1"), ("5,2", "4,1"), 
             ("3,2", "4,1"), ("7,1", "6,3"), ("0,4", "0,2"), ("7,0", "7,3"), ("0,3", "6,3"), 
             ("7,3", "6,3"), ("0,7", "0,3"), ("6,4", "5,4"), ("4,1", "6,3"), ("5,5", "6,3"), 
             ("2,1", "7,1"), ("6,3", "7,1"),  ("0,3", "7,3")]
    
    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()

    input_coords[0][0] = ("0,2")
    input_coords[0][1] = ("-1,-1")
    input_coords[0][2] = ("-1,-1")
    input_coords[0][3] = ("7,3")
    input_coords[0][4] = ("-1,-1")
    input_coords[0][5] = ("-1,-1")
    input_coords[0][6] = ("4,6")
    input_coords[0][7] = ("-1,-1")
    input_coords[0][11] = ("-1,-1")
    input_coords[0][12] = ("3,4")
    input_coords[1][1] = ("5,4")
    input_coords[1][2] = ("-1,-1")
    input_coords[1][4] = ("-1,-1")
    input_coords[1][5] = ("7,1")
    input_coords[1][6] = ("-1,-1")
    input_coords[1][9] = ("-1,-1")
    input_coords[1][10] = ("-1,-1")
    input_coords[1][11] = ("-1,-1")
    input_coords[1][12] = ("4,4")
    
    check_board_images(driver, input_coords, input_names)
    reset(driver)


def test_kasparov_topalov(driver):
    print("---------- test_kasparov_topalov ----------")
    login(driver)
    moves = [("1,4", "3,4"), ("6,3", "5,3"), ("1,3", "3,3"), ("7,6", "5,5"), ("0,1", "2,2"), 
             ("6,6", "5,6"), ("0,2", "2,4"), ("7,5", "6,6"), ("0,3", "1,3"), ("6,2", "5,2"),
             ("1,5", "2,5"), ("6,1", "4,1"), ("0,6", "1,4"), ("7,1", "6,3"), ("2,4", "5,7"),
             ("6,6", "5,7"), ("1,3", "5,7"), ("7,2", "6,1"), ("1,0", "2,0"), ("6,4", "4,4"),
             ("0,4", "0,2"), ("7,3", "6,4"), ("0,2", "0,1"), ("6,0", "5,0"), ("1,4", "0,2"),
             ("7,4", "7,2"), ("0,2", "2,1"), ("4,4", "3,3"), ("0,3", "3,3"), ("5,2", "4,2"),
             ("3,3", "0,3"), ("6,3", "5,1"), ("1,6", "2,6"), ("7,2", "7,1"), ("2,1", "4,0"),
             ("6,1", "7,0"), ("0,5", "2,7"), ("5,3", "4,3"), ("5,7", "3,5"), ("7,1", "6,0"),
             ("0,7", "0,4"), ("4,3", "3,3"), ("2,2", "4,3"), ("5,1", "4,3"), ("3,4", "4,3"),
             ("6,4", "5,3"), ("0,3", "3,3"), ("4,2", "3,3"), ("0,4", "6,4"), ("6,0", "5,1"),
             ("3,5", "3,3"), ("5,1", "4,0"), ("1,1", "3,1"), ("4,0", "3,0"), ("3,3", "2,2"),
             ("5,3", "4,3"), ("6,4", "6,0"), ("7,0", "6,1"), ("6,0", "6,1"), ("4,3", "3,2"),
             ("2,2", "5,5"), ("3,0", "2,0"), ("5,5", "5,0"), ("2,0", "3,1"), ("1,2", "2,2"),
             ("3,1", "2,2"), ("5,0", "0,0"), ("2,2", "1,3"), ("0,0", "1,1"), ("1,3", "0,3"),
             ("2,7", "0,5"), ("7,3", "1,3"), ("6,1", "6,3"), ("1,3", "6,3"), ("0,5", "3,2"),
             ("4,1", "3,2"), ("1,1", "7,7"), ("6,3", "2,3"), ("7,7", "7,0"), ("3,2", "2,2"),
             ("7,0", "3,0"), ("0,3", "0,4"), ("2,5", "3,5"), ("6,5", "4,5"), ("0,1", "0,2"),
             ("2,3", "1,3"), ("3,0", "6,0")]
    
    start(driver)
    apply_moves(driver, moves)
    input_names = reset_names()
    input_coords = reset_coords()

    input_coords[0][0] = ("0,2")
    input_coords[0][1] = ("6,0")
    input_coords[0][2] = ("-1,-1")
    input_coords[0][3] = ("-1,-1")
    input_coords[0][4] = ("-1,-1")
    input_coords[0][5] = ("-1,-1")
    input_coords[0][6] = ("-1,-1")
    input_coords[0][7] = ("-1,-1")
    input_coords[0][8] = ("-1,-1")
    input_coords[0][9] = ("-1,-1")
    input_coords[0][10] = ("-1,-1")
    input_coords[0][11] = ("-1,-1")
    input_coords[0][12] = ("-1,-1")
    input_coords[0][13] = ("3,5")
    input_coords[0][14] = ("2,6")
    input_coords[1][0] = ("0,4")
    input_coords[1][1] = ("-1,-1")
    input_coords[1][2] = ("1,3")
    input_coords[1][3] = ("-1,-1")
    input_coords[1][4] = ("-1,-1")
    input_coords[1][5] = ("-1,-1")
    input_coords[1][6] = ("-1,-1")
    input_coords[1][7] = ("-1,-1")
    input_coords[1][8] = ("-1,-1")
    input_coords[1][9] = ("2,2")
    input_coords[1][10] = ("-1,-1")
    input_coords[1][11] = ("-1,-1")
    input_coords[1][12] = ("-1,-1")
    input_coords[1][13] = ("4,5")
    input_coords[1][14] = ("5,6")
    
    check_board_images(driver, input_coords, input_names)
    resign(driver)
    reset(driver)


# Helpers
def apply_moves(driver, moves):
    for move in moves:
        retries = 3
        applied = False
        while retries > 0 and not applied:
            try:
                try:
                    source = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="{move[0]}"]'))
                    )
                except:
                    driver.save_screenshot("/static/screenshots/source_error.png")
                    print(driver.page_source)
                    raise
                
                source.click()
                time.sleep(0.5)
                try:
                    target = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="{move[1]}"]'))
                    )
                except:
                    driver.save_screenshot("/static/screenshots/target_error.png")
                    print(driver.page_source)
                    raise
                target.click()
                time.sleep(0.5)
                applied = True
            except StaleElementReferenceException:
                retries -= 1
                print(f"Retrying move {move} due to stale element")
            except Exception as e:
                print(f"Exception occurred during move {move}: {e}")
                raise


def getPieceImageUrl(type, color):
    match type:
        case 'Q':
            return 'http://localhost:8000/static/images/Qb.png' if color else 'http://localhost:8000/static/images/Qw.png'
        case 'K':
            return 'http://localhost:8000/static/images/Kb.png' if color else 'http://localhost:8000/static/images/Kw.png'
        case 'R':
            return 'http://localhost:8000/static/images/Rb.png' if color else 'http://localhost:8000/static/images/Rw.png'
        case 'B':
            return 'http://localhost:8000/static/images/Bb.png' if color else 'http://localhost:8000/static/images/Bw.png'
        case 'N':
            return 'http://localhost:8000/static/images/Nb.png' if color else 'http://localhost:8000/static/images/Nw.png'
        case 'P':
            return 'http://localhost:8000/static/images/Pb.png' if color else 'http://localhost:8000/static/images/Pw.png'
        case _:
            return 'http://localhost:8000/static/images/empty.png'


def reset_coords():
    coords_w = [("0,4"), ("0,3"), ("0,0"), ("0,7"), ("0,1"), ("0,6"), ("0,2"), ("0,5"), 
                ("1,0"), ("1,1"), ("1,2"), ("1,3"), ("1,4"), ("1,5"), ("1,6"), ("1,7")]
    coords_b = [("7,4"), ("7,3"), ("7,0"), ("7,7"), ("7,1"), ("7,6"), ("7,2"), ("7,5"), 
                ("6,0"), ("6,1"), ("6,2"), ("6,3"), ("6,4"), ("6,5"), ("6,6"), ("6,7")]
    return [coords_w, coords_b]


def reset_names():
    names_w = {
        0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
        8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
    }
    names_b = {
        0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
        8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
    }
    return [names_w, names_b]


def check_board_images(driver, coords_g, names_g):
    # piece id key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), 
    #             g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
    i=0
    for coords, names in zip(coords_g, names_g):
        for coord in coords:
            if coord != ("-1,-1"):
                print(f"TEST: coordinate checking: {coord}")
                square = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="{coord}"]'))
                )
                if square: 
                    try:
                        print(f"TEST: found square at {coord}")
                        img = WebDriverWait(square, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "img"))
                        )
                        img_src = img.get_attribute("src")
                        print(f"TEST: found image at {coord} url: {img_src}, calling pcURL with color: {i}")
                        expected_src = getPieceImageUrl(names[coords.index(coord)], i)
                        assert img_src == expected_src
                    except Exception as e:
                        print(f"Excpection occurred: {e}")
                        assert False, f"Image not found at coordinate {coord}"
        i+=1


def start(driver):
    try:
        start = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'start-button'))
        )
    except:
        driver.save_screenshot("/static/screenshots/start_error.png")
        print(driver.page_source)
        raise
    start.click()
    time.sleep(0.5)


def resign(driver):
    resign = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'resign-button'))
    )
    resign.click()
    time.sleep(0.5)


def reset(driver):
    reset = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'reset-button'))
    )
    reset.click()
    time.sleep(0.5)


def login(driver):
    driver.get(os.getenv("APP_URL", "http://localhost:8000/login"))
    print(f"Pre login driver URL: {driver.current_url}")
    # check if at login page (or redirected to login page from home page)
    if driver.current_url == "http://localhost:8000/login" or driver.current_url == "http://localhost:8000/login?next=%2F":
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        username_input.send_keys("valid_username")
        password_input.send_keys("valid_password")
        login_button.click()
    home_url = "http://localhost:8000/"
    print(f"Post login driver URL: {driver.current_url}, expected: {home_url}, equal: {driver.current_url == home_url}")
    WebDriverWait(driver, 10).until(EC.url_to_be(home_url))

def register_testuser(driver):
    register_url = "http://localhost:8000/register"
    driver.get(register_url)
    print(f"Accessing {register_url}")
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
        register_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        print("Found registration form elements")
        username_input.send_keys("valid_username")
        password_input.send_keys("valid_password")
        register_button.click()
    except TimeoutException as e:
        print(f"TimeoutException: {e}")
        screenshot_path = "/static/screenshots/register_timeout.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        raise
