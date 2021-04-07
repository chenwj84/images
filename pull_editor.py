# -*- coding: utf-8 -*-

import config
import utils

# ========== Start Settings ==========
EDITOR_TRUNK = "editor_trunk"
EDITOR_DEV = "editor_dev"
EDITOR_TRUNK_OUT = "editor_trunk_out"
EDITOR_RELEASE = "editor_release"
EDITOR_TRUNK_RES = "editor_trunk_res"
EDITOR_TRUNK_ADVANCE = "editor_trunk_advance"
EDITOR_TRUNK_4231 = "editor_trunk_4231"

EDITOR_BRANCH_SPECIAL = {
    EDITOR_TRUNK_4231 : "ue4231",
}

EDITOR_POST_NAME = {
    EDITOR_TRUNK_OUT : "out",
    EDITOR_TRUNK_RES : "res",
    EDITOR_TRUNK_ADVANCE : "advance",
}

ENGINE_POST_NAME = {
    EDITOR_TRUNK_OUT : "out",
    EDITOR_TRUNK_ADVANCE : "advance",
}

EDITOR_DDC_PATH = {
    EDITOR_TRUNK_RES : "GIH-D-15667\\DDCRes",
}

EDITOR_SVN_PATH = {
    EDITOR_TRUNK : (config.build_client_svn, config.build_engine_svn),
    EDITOR_DEV : (config.build_client_dev_svn, config.build_engine_dev_svn),
    EDITOR_TRUNK_OUT : (config.build_client_out_svn, config.build_engine_out_svn),
    EDITOR_RELEASE : (config.build_client_release_svn, config.build_engine_release_svn),
    EDITOR_TRUNK_RES : (config.build_client_res_svn, config.build_engine_svn),
    EDITOR_TRUNK_ADVANCE: (config.build_client_advance_svn, config.build_engine_advance_svn),
    EDITOR_TRUNK_4231 : (config.build_client_ue4231_svn, config.build_engine_ue4231_svn),
}
# ========== End Settings ==========


# =====================
# argv : [branch, sub_branch, rename]
# branch : 分支名称
# sub_branch : editor的不同版本，如editor_res为res,editor_out为out，输入空或‘none’ 默认为editor项目
# rename : 是否需要将已有的文件rename，默认为True，否定为传入“False”
# =====================
def main(argv):
    branch = argv[0]

    project_name = "editor"
    project_key = "editor_%s" % branch
    if len(argv) >= 2 and argv[1] != 'none':
        project_name = "%s_%s" % (project_name, argv[1])
        project_key = "%s_%s" % (project_key, argv[1])

    if project_key not in EDITOR_SVN_PATH:
        print("%s 的svn目录不存在" % project_name)
        return

    if len(argv) >= 3 and argv[2] == "False":
        PullEditor(branch, project_name, project_key, False)
    else:
        PullEditor(branch, project_name, project_key)

def PullEditor(branch, project_name, project_key, rename = True):
    if project_key in EDITOR_POST_NAME:
        client_project_path = "editor_%s" % EDITOR_POST_NAME[project_key]
    else:
        client_project_path = "editor"

    if project_key in ENGINE_POST_NAME:
        engine_project_path = "engine_%s" % ENGINE_POST_NAME[project_key]
    else:
        engine_project_path = "engine"

    if project_key in EDITOR_BRANCH_SPECIAL:
        branch = "%s/%s" % (EDITOR_BRANCH_SPECIAL[project_key], branch)

    client_path = "%s/%s/%s" % (config.root, branch, client_project_path)
    engine_path = "%s/%s/%s" % (config.root, branch, engine_project_path)

    if rename:
        client_rename_path = client_path + "_useless"
        engine_rename_path = engine_path + "_useless"

        utils.CheckAndMoveOldVersion(client_path, client_rename_path)
        utils.CheckAndMoveOldVersion(engine_path, engine_rename_path)

    branch_path = "%s/%s" % (config.project_path, branch)
    utils.MakeDirIfNotExist(branch_path)

    client_svn_path, engine_svn_path = EDITOR_SVN_PATH[project_key]
    client_switch_flag=utils.UpdateOrCheckoutSVN(client_path, client_svn_path)
    if project_key == "editor_release":
        content_path = client_path+"/Content"
        content_switch_flag=utils.UpdateOrCheckoutSVN(content_path, config.build_art_release_svn)
    engine_switch_flag=utils.UpdateOrCheckoutSVN(engine_path, engine_svn_path)

    if project_key == "editor_release":
        if client_switch_flag or content_switch_flag or engine_switch_flag:
            utils.CheckReleaseInfo()

    if project_key in EDITOR_DDC_PATH:
        utils.ModifyShareDDCConfig(client_path, EDITOR_DDC_PATH[project_key])
