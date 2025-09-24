# Kontext Hack - Perspective Grid Generator with AI

![Screenshot of the Perspective Grid Generator web app](media/SCR-20250924-uemn.png)


A web application that generates perspective grids and uses them to create AI-generated images with proper perspective.

## Lora 
The model can be found: https://huggingface.co/jschoormans/flux-kontext-dev-vanishing-point-lora 

## Training 
This LoRa was trained on 1063 image pairs and captions. 

Data and vanishing point annotations are from the AVA Dataset, and the vanishing point data is courtesy of:

Detecting Dominant Vanishing Points in Natural Scenes with Application to Composition-Sensitive Image Retrieval  
Zihan Zhou, Farshid Farhat, and James Z. Wang  
IEEE Transactions on Multimedia, 2017. [https://zihan-z.github.io/projects/vpdetection/]

The dataset can be found here: https://huggingface.co/datasets/jschoormans/perspective_control/tree/main

The LoRa was trained using the AI Toolkit.

## Inference
Trigger word: "vanpoint". Create control images like the ones in the dataset, using the process_vanishing_points.py script or with the interactive web app.


## Web app 



1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory with your FAL API key:
```
FAL_KEY=your_fal_key_here
```

3. Start the server:
```bash
npm start
```

4. Open your browser to `http://localhost:3000`

## Usage

1. Click on the canvas to set a vanishing point
2. Enter a prompt in the text field (e.g., "vanpoint cityscape")
3. Click "Generate Image" to create an AI-generated image using your perspective grid
4. Wait for the generation to complete (this may take a few minutes)

## API Endpoints

- `POST /api/generate` - Submit image generation request
- `GET /api/status/:requestId` - Check generation status

## Dependencies

- Express.js for the server
- FAL API for AI image generation
- Custom LoRA model for perspective-aware generation

## Deployment

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
vercel
```

3. **Set environment variables in Vercel dashboard:**
   - `FAL_API_KEY` = your FAL API key

### Option 2: Railway

1. **Connect your GitHub repository to Railway**
2. **Set environment variables:**
   - `FAL_API_KEY` = your FAL API key
3. **Deploy automatically on push**

### Option 3: Render

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Set environment variables:**
   - `FAL_API_KEY` = your FAL API key
4. **Deploy**

### Option 4: Heroku

1. **Install Heroku CLI**
2. **Create Heroku app:**
```bash
heroku create your-app-name
```

3. **Set environment variables:**
```bash
heroku config:set FAL_API_KEY=your_fal_key_here
```

4. **Deploy:**
```bash
git push heroku main
```

### Environment Variables

Make sure to set the following environment variable in your deployment platform:
- `FAL_API_KEY` - Your FAL API key for image generation

### Production Notes

- The app uses port 3000 by default, but most platforms will set the `PORT` environment variable
- Make sure your FAL API key has sufficient credits for image generation
- The app handles CORS for cross-origin requests



