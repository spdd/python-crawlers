require 'torch'
require 'nn'
require 'image'

require 'fast_neural_style.ShaveImage'
require 'fast_neural_style.TotalVariation'
require 'fast_neural_style.InstanceNormalization'
local utils = require 'fast_neural_style.utils'
local preprocess = require 'fast_neural_style.preprocess'

--[[
Use a trained feedforward model to stylize either a single image or an entire
directory of images.
--]]

local cmd = torch.CmdLine()

-- Model options
cmd:option('-model', 'models/instance_norm/candy.t7')
cmd:option('-image_size', 512)
cmd:option('-median_filter', 3)
cmd:option('-timing', 0)
cmd:option('-txt', 0)
cmd:option('-python', '')

-- Input / output options
cmd:option('-input_image', 'lena.png')
cmd:option('-output_image', 'out.png')

local function main()
  local opt = cmd:parse(arg)

  print('test from python ' .. opt.python)
  print('model: ' .. opt.model)
  print('input image: ' .. opt.input_image)
  print('output image: ' .. opt.output_image)

  local dtype = 'torch.FloatTensor'
  local ok, checkpoint = pcall(function() return torch.load(opt.model) end)
  if not ok then
    print('ERROR: Could not load model from ' .. opt.model)
    print('You may need to download the pretrained models by running')
    print('bash models/instance_norm/download_models.sh')
    return
  end
  local model = checkpoint.model
  model:evaluate()
  model:type(dtype)

  local preprocess_method = checkpoint.opt.preprocessing or 'vgg'
  local preprocess = preprocess[preprocess_method]
  
  local function run_image(in_path, out_path)
    local img = image.load(in_path, 3)
    if opt.image_size > 0 then
      img = image.scale(img, opt.image_size)
    end
    local H, W = img:size(2), img:size(3)
    
    local img_pre = preprocess.preprocess(img:view(1, 3, H, W)):type(dtype)
    local timer = nil
    if opt.timing == 1 then
      -- Do an extra forward pass to warm up memory and cuDNN
      model:forward(img_pre)
      timer = torch.Timer()
    end
    local img_out = model:forward(img_pre)

    local img_out = preprocess.deprocess(img_out)[1]

    if opt.median_filter > 0 then
      img_out = utils.median_filter(img_out, opt.median_filter)
    end

    print('Writing output image to ' .. out_path)
    image.save(out_path, img_out)
  end
  run_image(opt.input_image, opt.output_image)
end

main()

