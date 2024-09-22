

from PIL import Image, ImageSequence


def unpack_gif(src):
    # Load Gif
    image = Image.open(src)

    # Get frames and disposal method for each frame
    frames = []
    disposal = []
    for gifFrame in ImageSequence.Iterator(image):
        disposal.append(gifFrame.disposal_method)
        frames.append(gifFrame.convert('P'))

    # Loop through frames, and edit them based on their disposal method
    output = []
    lastFrame = None
    thisFrame = None
    for i, loadedFrame in enumerate(frames):
        # Update thisFrame
        thisFrame = loadedFrame
        print(disposal[i])
        # If the disposal method is 2
        if disposal[i] == 2:
            # Check that this is not the first frame
            if i != 0:
                # Pastes thisFrames opaque pixels over lastFrame and appends lastFrame to output
                lastFrame.paste(thisFrame, mask=thisFrame.convert('RGBA'))
                output.append(lastFrame)
            else:
                output.append(thisFrame)

        # If the disposal method is 1 or 0
        elif disposal[i] == 1 or disposal[i] == 0:
            # Appends thisFrame to output
            output.append(thisFrame)
            
        # If disposal method if anything other than 2, 1, or 0
        else:
            raise ValueError('Disposal Methods other than 2:Restore to Background, 1:Do Not Dispose, and 0:No Disposal are supported at this time')

        # Update lastFrame
        lastFrame = loadedFrame
        #output.save(save_path, save_all=True)
    return output


    

gif = r"C:\Downloads\[NEKO WORKs] Neko Para Vol. 4 Neko to Patissier no Noel [GIF + MP4 + WebM]\GIF\neko4_h02c1a.gif"
save_path = r"C:\Downloads\[NEKO WORKs] Neko Para Vol. 4 Neko to Patissier no Noel [GIF + MP4 + WebM]\001.gif"

unpack_gif(gif)
