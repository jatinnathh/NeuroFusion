
#  NeuroFusion

**NeuroFusion** is a modern mobile application built with **React Native (Expo)** that allows users to generate AI-powered images using both **text-to-image** and **image-to-image** diffusion techniques. This project was developed during my internship at **Innova Solutions**.

##  Features

-  **Text-to-Image**: Generate AI art from written prompts using a custom Stable Diffusion pipeline.
-  **Image-to-Image**: Transform existing images based on new prompts or styles.
-  **Prompt Queueing**: All image generation requests are queued and processed sequentially.
-  **Cancel Generation**: Users can cancel pending or in-progress image generation tasks from their queue.
-  Built with **Expo** for seamless deployment across Android, iOS, and Web.
-  FastAPI backend for image processing, queuing, and cancellation logic.
-  Integrated **CLIP Tokenizer** + Custom **UNet-based Diffusion Model** for high-quality generation.

##  Tech Stack

- **Frontend**: React Native (Expo), React Navigation
- **Backend**: Python, FastAPI, PyTorch, Custom Stable Diffusion
- **Database**: MySQL / SQLite 
- **Cloud**: Docker 

##  App Overview and working
> [Watch Web Demo (Download/View)](https://raw.githubusercontent.com/jatinnathh/NeuroFusion/main/static/assets/web_neuro%20(1).mp4)


##  Example Generations
![Image](https://github.com/user-attachments/assets/2e664f49-05cb-4172-b9db-70ffc4fe66d6)
##  How to Run (Local Dev)

```bash
# Clone the repo
git clone https://github.com/jatinnathh/NeuroFusion.git
cd NeuroFusion

# Start Expo frontend
python update_ip.py
netsh advfirewall firewall add rule name="Allow Port 8000" dir=in action=allow protocol=TCP localport=8000
docker compose up --build 

```


## Reference papers

- Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/pdf/2112.10752). 
- Ho, J., Jain, A., & Abbeel, P. (2020). [Denoising Diffusion Implicit Models](https://arxiv.org/pdf/2006.11239).


