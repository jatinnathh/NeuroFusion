
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

##  Example Generations
<img src="https://github.com/user-attachments/assets/2e664f49-05cb-4172-b9db-70ffc4fe66d6" width="300"/>

<img src="https://github.com/user-attachments/assets/0339625d-03d0-404d-88dd-bc9b2415ef08" width="300"/>
<img src="https://github.com/user-attachments/assets/f594154f-392d-4d43-ac78-f283a5302f59" width="300"/>
<img src="https://github.com/user-attachments/assets/e4f48635-e39e-4bfd-9c3d-4642794b3c49" width="300"/>
<img src="https://github.com/user-attachments/assets/b56904ef-b78c-46e6-855e-c541019a423a" width="300"/>
<img src="https://github.com/user-attachments/assets/a680e117-b572-4b19-a17b-06da2ca6a1d0" width="300"/>
<br/>
<br/>
<br/>

**Below are a few example outputs generated using the same prompt. Differences in images arise due to changes in hyperparameters.**

<img width="1204" height="621" alt="Image" src="https://github.com/user-attachments/assets/cb166f56-7206-4609-b21d-8ea10f5b8b96" />


<img width="1199" height="612" alt="Image" src="https://github.com/user-attachments/assets/5c3ba0b9-5ddc-45d0-8b79-42e2beb60211" />



##  App Overview and working
> [Watch Web Demo (Download/View)](https://github.com/user-attachments/assets/4dfeb53a-b648-4bef-9265-82cfb9ad1df7)

> [Watch Mobile Demo (Download/View)](https://github.com/user-attachments/assets/e8cfd03a-a0ef-413e-98a9-2ec217bc2880)



# Clone the repo
git clone https://github.com/jatinnathh/NeuroFusion.git

cd NeuroFusion

# Start Expo frontend
python update_ip.py

netsh advfirewall firewall add rule name="Allow Port 8000" dir=in action=allow protocol=TCP localport=8000

docker compose up --build


## Reference papers

- Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/pdf/2112.10752). 
- Ho, J., Jain, A., & Abbeel, P. (2020). [Denoising Diffusion Implicit Models](https://arxiv.org/pdf/2006.11239).
