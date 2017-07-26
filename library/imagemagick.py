#! /usr/bin/env python
# coding=utf-8
__author__ = 'Xuxh'

import subprocess
import desktop


def get_cmd_name():

    cmd_name = ''

    os_name = desktop.get_desktop_os_type()

    if os_name == 'Windows':
        cmd_name = 'im_convert'
    else:
        cmd_name = 'convert'

    return cmd_name


def execute_cmds(cmds,debug=False):

    ret = ''
    if type(cmds) == str:
        cmds = [cmds]
    for cmd in cmds:
        if debug:
            print 'Execute command: {}'.format(cmd)
        ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ret.wait()
        if ret.returncode != 0:
            return ret
    return ret


def crop_image(img_path, width, height, x, y, output_path='crop_img.jpg'):

    cmd_name = get_cmd_name()
    cmds = [
    '{} {} -crop {}x{}+{}+{} {}'.format(cmd_name, img_path, width, height, x, y,
                                        output_path)
    ]
    ret = execute_cmds(cmds)
    return ret


def resize_image(img_path, width, height, output_path):

    cmd_name = get_cmd_name()

    cmds = [
    '{} {} -resize {}x{} {}'.format(cmd_name, img_path, width, height, output_path)
    ]
    ret = execute_cmds(cmds)
    return ret


def identify_image(img_path):

    cmds = ['identify {}'.format(img_path)]
    ret = execute_cmds(cmds)
    return ret


def overlap_image(orig_img, overlay_img, dest_img):

    cmd_name = get_cmd_name()

    cmds = [
    '{} {} -compose over {} -composite {}'.format(cmd_name, orig_img, overlay_img, dest_img)
    ]

    ret = execute_cmds(cmds)
    return ret


def add_backgound(orig_img,rgb_color,dest_img):

    cmd_name = get_cmd_name()

    cmds = [
    '{} {} -background {} -flatten {}'.format(cmd_name, orig_img, rgb_color, dest_img)
    ]

    ret = execute_cmds(cmds)
    return ret


def make_image_gray(img_path, gray_img):

    cmd_name = get_cmd_name()

    cmds = [
        '{} {} -type Grayscale -depth 4 {}'.format(img_path, gray_img),
    ]
    ret = execute_cmds(cmds)
    return ret


# just for separate transparent image, remove alpha
def separate_image(orig_img,dest_img):

    cmd_name = get_cmd_name()

    cmds = [
        '{} {}  -background black -alpha remove {}'.format(orig_img, dest_img),
    ]
    ret = execute_cmds(cmds)
    return ret


# the most better method to make gray image at first, then compare
def compare_image(actu_image,expe_image):

    cmds = [
    'compare -metric AE -fuzz 20% {} {} similar.jpg'.format(actu_image, expe_image),
    ]
    ret = execute_cmds(cmds)

    try:

        value = int(ret.stdout.readline())
        if value < 150:
            return True
    except Exception,ex:
        print ex

    return False




def detect_sub_image(sub_img_path, sub_x, sub_y, search_img_path,
                 search_width, search_height, search_x, search_y):

    sub_gray_img = 'sub_gray_img.jpg'
    search_gray_img = 'search_gray_img.jpg'
    crop_img = 'crop_img.jpg'

    ret = make_image_gray(sub_img_path, sub_gray_img)
    if ret.status_code != 0:
        return False

    ret = make_image_gray(search_img_path, search_gray_img)
    if ret.status_code != 0:
        return False

    ret = crop_image(search_gray_img, search_width, search_height, search_x,
                     search_y)
    if ret.status_code != 0:
        return False

    cmds = [
        'compare -channel black -metric RMSE -subimage-search {} {} similar.png'.
        format(crop_img, sub_gray_img)
    ]

    # see if the v logo detection is correct
    ret = execute_cmds(cmds)
    if ret.status_code != 0:
        return False
    ret_str = ret.std_err
    pos_x, pos_y = [int(x) for x in ret_str.split(' ')[-1].split(',')]
    if pos_x != (sub_x - search_x) or pos_y != (sub_y - search_y):
        return False

    return True

if __name__ == '__main__':

    #resize_image(r'E:\test.png',1080,1475,r'E:\test9.png')
    #result = detect_sub_image(r'E:\test9.png',200,300,r'E:\screen0.png',1080,1475,0,0)
    img1 = r'E:\aimg.png'
    img2 = r'E:\eimg.png'
    result = compare_image(img1,img2)
    print result