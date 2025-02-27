# Senza

**Element Framework for PyScript**

## IMPORTANT!
I have broken the orginal project up, so the core senza library is more modular and could be more easily used across frameworks. 
The orginal fastapi starter project is now senza-fastapi. 
https://github.com/Phelsong/senza-fastapi 

This repo meant to run as a (sub)module 

## What is Senza?

senza is a lightweight wrapper around the dom api already offered with pyscript, with a few added features, namely: 
- Composable ui elements 
- End-to-end type annotations 
- A lightweight DOM router, for quickly building page navigation 
- A more through websocket implementation 
- Flexbox support
- web compiler/minifier [wip]

It it targeted toward local apps or small web apps, with a focus on simplicity and ease of use. 

(Some) Planned features:
- Improved error handling and logging
- Support for more complex UI elements
- Integration with other frameworks and libraries
- Mojo Wrapper/Hooks

## How to use
At the project root 
__git submodule add https://github.com/Phelsong/senza.git ./senza__ 

(there will be package releases as the project is more throughly fleshed out)
