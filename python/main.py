import itertools, math, os, pygame, sys
from security_camera import *
from solver import *

WINDOW_WIDTH = 824
WINDOW_HEIGHT = 640
BITMAP_SCALE = 8
BITMAP_WIDTH = WINDOW_WIDTH // BITMAP_SCALE
BITMAP_HEIGHT = WINDOW_HEIGHT // BITMAP_SCALE
COLOR_BLACK = pygame.Color(0,0,0)
ASSET_PATH = "assets"
TEXTURE_FILENAMES = [
  [
    [ "sample_floor.png" ],
    [ "sample_bitmap.png" ],
    [ "sample_bitmap_full.png" ],
  ],
  [
    [ "floor1.png", "floor2.png", "floor3.png" ],
    [ "floor_bitmap1.png", "floor_bitmap2.png", "floor_bitmap3.png" ],
    [ "floor_bitmap_full1.png", "floor_bitmap_full2.png", "floor_bitmap_full3.png" ],
  ],
  [
    ["square.png","circle.png"],
    ["square_mini.png","circle_mini.png"],
    ["square.png","circle.png"],
  ],
    [
    ["224_grid.png","56_grid.png","16_grid.png","4_grid.png"],
    ["224_grid_mini.png","56_grid_mini.png","16_grid_mini.png","4_grid_mini.png"],
    ["224_grid.png","56_grid.png","16_grid.png","4_grid.png"],
  ]
]

# TODO: Try adjusting the field of view to see how it affects the number of cameras required.
FOV = [90]
num_cam_fovs = []
# TODO: 0 = sample textures, 1 = Isabella Stewart Gardner museum, feel free to add more.
TEXTURE_SET = 2

def load_asset(path):
  return pygame.image.load(os.path.join(ASSET_PATH, path))

currentFloor = 0
floorTextureFilenames = TEXTURE_FILENAMES[TEXTURE_SET][0]
bitmapTextureFilenames = TEXTURE_FILENAMES[TEXTURE_SET][1]
bitmapFullTextureFilenames = TEXTURE_FILENAMES[TEXTURE_SET][2]
numberFloors = len(floorTextureFilenames)
floorImages = []
floorBitmaps = []
floorBitmapsFull = []
securityCameras = []

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
securityCameraImage = load_asset("security_camera.png")
for fieldOfView in range(len(FOV)):
  for i in range(numberFloors):
    floorImages.append(load_asset(floorTextureFilenames[i]))
    bitmapImage = load_asset(bitmapTextureFilenames[i])
    bitmapFullImage = load_asset(bitmapFullTextureFilenames[i])

    bitmap = []
    for x in range(BITMAP_WIDTH):
      column = []
      for y in range(BITMAP_HEIGHT):
        column.append(bitmapImage.get_at((x,BITMAP_HEIGHT-y-1)) == COLOR_BLACK)
      bitmap.append(column)
    floorBitmaps.append(bitmap)

    bitmapFull = []
    for x in range(WINDOW_WIDTH):
      column = []
      for y in range(WINDOW_HEIGHT):
        column.append(bitmapFullImage.get_at((x,WINDOW_HEIGHT-y-1)) == COLOR_BLACK)
      bitmapFull.append(column)
    floorBitmapsFull.append(bitmapFull)

    scaledCameras = []
    count = 0
    for camera in solve(bitmap, FOV[fieldOfView]):
      count = count+1
      scaledCamera = SecurityCamera(
        camera.x * BITMAP_SCALE,
        (camera.y +1) * BITMAP_SCALE,
        FOV[fieldOfView],
        camera.direction,
        bitmapFull
      )
      scaledCameras.append(scaledCamera)
    num_cam_fovs.append(count)
    securityCameras.append(scaledCameras)

# print(num_cam_fovs)
while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
    if event.type == pygame.KEYDOWN:
      # if event.key == pygame.K_UP:
      if event.key == pygame.K_d:
        currentFloor = min(numberFloors-1, currentFloor+1)
      # elif event.key == pygame.K_DOWN:
      elif event.key == pygame.K_a:
        currentFloor = max(0, currentFloor-1)

  image = floorImages[currentFloor]
  screen.blit(image, image.get_rect())
  for camera in securityCameras[currentFloor]:
    camera.render(screen)
  for camera in securityCameras[currentFloor]:
    image = pygame.transform.rotate(securityCameraImage, camera.direction)
    rect = image.get_rect()
    rect = rect.move(camera.x - rect.width//2, WINDOW_HEIGHT-(camera.y+rect.height//2)-1)
    screen.blit(image, rect)

  pygame.display.flip()
  clock.tick(60)
