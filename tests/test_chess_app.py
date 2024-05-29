import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    driver.get(os.getenv("APP_URL", "http://localhost:5000"))
    yield driver
    driver.quit()


def test_page_title(driver):
    assert "Chess" in driver.title


def test_play_chess(driver):
    moves = [("1,4", "3,4"), ("6,4", "4,4"), ("0,6", "2,5"), ("7,1", "5,2")]
    start(driver)
    for move in moves:
        source = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="{move[0]}"]'))
        )
        target = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="{move[1]}"]'))
        )
        source.click()
        time.sleep(0.5)
        target.click()
        time.sleep(0.5)
    input_coords = reset_coords()
    input_coords[0][5] = ("2,5")
    input_coords[0][12] = ("3,4")
    input_coords[1][4] = ("5,2")
    input_coords[1][12] = ("4,4")
    input_names = reset_names()
    check_board_images(driver, input_coords, input_names)
    resign(driver)
    reset(driver)


def test_invalid_move(driver):
    start(driver)
    source = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="1,4"]'))
        )
    target = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-coordinate="4,4"]'))
        )
    source.click()
    time.sleep(0.5)
    target.click()
    time.sleep(0.5)
    input_coords = reset_coords()
    input_names = reset_names()
    check_board_images(driver, input_coords, input_names)
    resign(driver)
    reset(driver) 


# Helpers
def getPieceImageUrl(type, color):
    match type:
        case 'Q':
            return 'http://localhost:5000/static/images/Qb.png' if color else 'http://localhost:5000/static/images/Qw.png'
        case 'K':
            return 'http://localhost:5000/static/images/Kb.png' if color else 'http://localhost:5000/static/images/Kw.png'
        case 'R':
            return 'http://localhost:5000/static/images/Rb.png' if color else 'http://localhost:5000/static/images/Rw.png'
        case 'B':
            return 'http://localhost:5000/static/images/Bb.png' if color else 'http://localhost:5000/static/images/Bw.png'
        case 'N':
            return 'http://localhost:5000/static/images/Nb.png' if color else 'http://localhost:5000/static/images/Nw.png'
        case 'P':
            return 'http://localhost:5000/static/images/Pb.png' if color else 'http://localhost:5000/static/images/Pw.png'
        case _:
            return 'http://localhost:5000/static/images/empty.png'


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
    start = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'start-button'))
        )
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