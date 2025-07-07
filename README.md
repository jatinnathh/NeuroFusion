
#  NeuroFusion

**NeuroFusion** is a modern mobile application built with **React Native (Expo)** that allows users to generate AI-powered images using both **text-to-image** and **image-to-image** diffusion techniques. This project was developed during my internship at **Innova Solutions**.

##  Features

-  **Text-to-Image**: Generate AI art from written prompts using a custom Stable Diffusion pipeline.
- 🖼 **Image-to-Image**: Transform existing images based on new prompts or styles.
-  Built with **Expo** for seamless deployment across Android, iOS, and Web.
-  FastAPI backend for image processing and queue management.
-  CLIP Tokenizer + Custom UNet-based Diffusion Model integration.

##  Tech Stack

- **Frontend**: React Native (Expo), React Navigation
- **Backend**: Python, FastAPI, PyTorch, Custom Stable Diffusion
- **Database**: MySQL / SQLite 
- **Cloud**: Docker 

##  Screenshots

> _Add screenshots here if needed (e.g., generation screen, queue, admin panel)_

##  How to Run (Local Dev)

```bash
# Clone the repo
git clone https://github.com/jatinnathh/NeuroFusion.git
cd NeuroFusion

# Start Expo frontend
python update_ip.py
netsh advfirewall firewall add rule name="Allow Port 8000" dir=in action=allow protocol=TCP localport=8000
docker compose up --build 


