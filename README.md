# Yandere Downloader

## Introduction
Yandere Downloader is a simple command line program to download images from the [Yande.re website](https://yande.re). The program is written in Python 3.

![image001.png](/images/image001.png)

## Requirements
The following package is required:
   * bs4
   * requests

## Features
* Download by Image ID, Pool ID, Tag and User

## Instructions
* Execute `run.py` on Command Prompt (or Terminal in Mac).
* Option 1: Download by Image ID:
    * Input `3` to download image ID 3.
    * Input `2-5` to download image ID 2 to 5.
    * Input `5,8` to download image ID 5 and 8.
    * Input `2-5,7,9-11` to download image ID 2, 3, 4, 5, 7, 9, 10, 11
    * Example of image ID: `737516` from `https://yande.re/post/show/737516`
* Option 2: Download by Pool ID:
    * Just specify the Pool ID (e.g. `97960` from `https://yande.re/pool/show/97670`)
    * Specify the range of image ID to download
        * Input `0` to download all
* Option 3: Download by tag:
    * E.g. `dress` from `https://yande.re/post?tags=dress`
* Option 4: Download by user:
    * E.g. `drop` from `https://yande.re/post?tags=user%3Adrop` (after `user%3A`)
