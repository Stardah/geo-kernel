class Commands:

    # commands and its arguments for map object
    mapCommands = {"create": ["-map", "-x", "-y", "-zoom"],
                   "show": ["-map"],
                   "delete": ["-map"],
                   "update": ["-map", "-name", "-x", "-y", "-zoom"],
                   "login": []
                   }
    # commands and its arguments for layer object
    layerCommands = {"create": ["-map", "-layer", "-link"],
                     "show": ["-map", "-layer"],
                     "delete": ["-map", "-layer"],
                     "update": ["-map", "-layer", "-name", "-link"],
                     "login": []
                     }

    # GDAL commands
    gdalCommands = {
        "gdalinfo": ["-json", "-mm", "-stats", "-hist", "-nogcp", "-nomd", "-norat",
                     "-noct", "-nofl", "-checksum", "-proj4", "-listmdd",
                     "-mdd", "-wkt_format", "-sd", "-oo"],
        "gdal_translate": ["-ot", "-of", "-b", "-mask", "-expand", "-outsize",
                           "-tr", "-r", "-unscale", "-scale", "-exponent",
                           "-srcwin", "-epo", "-eco", "-projwin", "-projwin_srs",
                           "-a_srs", "-a_ullr", "-a_nodata", "-a_scale", "-a_offset",
                           "-nogcp", "-gcp", "-colorinterp", "-mo", "-q", "-co",
                           "-sds", "-stats", "-norat", "-oo"],
        "gdalwarp": ["-s_srs", "-t_srs", "-ct", "-to", "-novshiftgrid", "-order",
                     "-et", "-refine_gcps", "-te", "-te_srs", "-tr", "-ts",
                     "-tap", "-ovr", "-wo", "-ot", "-wt", "-srcnodata",
                     "-dstnodata", "-srcalpha", "-nosrcalpha", "-dstalpha", "-r",
                     "-wm", "-multi", "-q", "-cutline", "-cl", "-cwhere",
                     "-csql", "-cblend", "-crop_to_cutline", "-oo", "-of", "-co",
                     "-overwrite", "-nomd", "-cvmd", "-setci", "-doo"],
    }

    gdalArguments = {
        "-mdd": ["domain", "`all`"],
        "-wkt_format": ["WKT", "WKT1", "WKT2"],
        "-ot": ["Byte", "Int16", "UInt16", "UInt32", "Int32", "Float32", "Float64",
                "CInt16", "CInt32", "CFloat32", "CFloat64"],
        "-wt": ["Byte", "Int16", "UInt16", "UInt32", "Int32", "Float32", "Float64",
                "CInt16", "CInt32", "CFloat32", "CFloat64"],
        "-expand": ["gray", "rgb", "rgba"],
        "-r": ["nearest", "bilinear", "cubic", "cubicspline", "lanczos", "average", "mode"],
        "-colorinterp": ["red", "green", "blue", "alpha", "gray", "undefined"],
        "-order": ["n", "-tps", "-rpc", "-geoloc"],
    }

    # list of CRUD commands for both map and layer objects
    commonComands = ["create", "show", "delete", "update", "gdalinfo", "gdal_translate", "gdalwrap"]
    words = ["layer", "map", "gdal"]
    # dict of command's descriptions
    inspections = {
        "map show": "Returns an html document containing the map with all its layers\n  [-map]:string",
        "map create": "Creates new map with name [-map]\n [-map]:string [-x]:double [-y]:double [-zoom]:int",
        "map update": "Changes map attributes\n Required: [-map]:string\n Optional: [-name]:string [-x]:double [-y]:double [-zoom]:int",
        "map delete": "Deletes map\n [-map]:string",
        "layer show": "Returns a string of layer attributes",
        "layer create": "Adds new layer [-layer] to a map [-map]\n [-layer]:string [-map]:string",
        "layer update": "Changes layer attributes\n Required: [-layer]:string\n Optional: [-name]:string [-link]:string",
        "layer delete": "Removes layer\n [-layer]:string",
        "gdal_translate": "[-ot type] [-strict] [-of format] [-b band]*\n\
           [-mask band] [-expand clr] [-outsize xsize[%]|0 ysize[%]|0] [-tr xres yres]\n\
           [-r  resampling_algorithm] [-unscale] [-scale[_bn]\n\
           [src_min src_max [dst_min dst_max]]]* [-exponent[_bn] exp_val]*\n\
           [-srcwin] [-epo] [-eco] [-projwin] [-projwin_srs srs_def] [-a_srs srs_def] [-a_ullr]\n\
           [-a_nodata value] [-a_scale value] [-a_offset value] [-nogcp]\n\
           [-mo META-TAG=VALUE]* [-q] [-sds] [-co NAME=VALUE]* [-stats] [-norat]\n\
           [-colorinterp color] [-gcp pixel line easting northing [elevation]]*\n\
           [-oo NAME=VALUE]* src_dataset dst_dataset",
        "gdalinfo": "[-json] [-mm] [-stats] [-hist] [-nogcp] [-nomd]\n\
            [-norat] [-noct] [-nofl] [-checksum] [-proj4]\n\
            [-listmdd] [-mdd domain|`all`]* [-wkt_format WKT1|WKT2|...]\n\
            [-sd subdataset] [-oo NAME=VALUE]* datasetname",
        "gdalwarp": "[-s_srs srs_def] [-t_srs srs_def] [-ct string] [-to NAME=VALUE]*\n\
               [-novshiftgrid] [-order n | -tps | -rpc | -geoloc] [-et err_threshold]\n\
               [-refine_gcps tolerance [minimum_gcps]] [-te xmin ymin xmax ymax]\n\
               [-te_srs srs_def] [-tr xres yres] [-tap] [-ts width height]\n\
               [-ovr level|AUTO|AUTO-n|NONE] [-wo NAME=VALUE] [-ot Byte/Int16/...]\n\
               [-wt Byte/Int16] [-srcnodata value] [-dstnodata value]\n\
               [-srcalpha|-nosrcalpha] [-dstalpha] [-r resampling_method] [-wm memory_in_mb]\n\
               [-multi] [-q] [-cutline datasource] [-cl layer] [-cwhere expression]\n\
               [-csql statement] [-cblend dist_in_pixels] [-crop_to_cutline]\n\
               [-of format] [-co NAME=VALUE]* [-overwrite] [-nomd] \n\
               [-cvmd meta_conflict_value] [-setci] [-oo NAME=VALUE]*\n\
               [-doo NAME=VALUE]* srcfile* dstfile"
    }

    objects = {
        "map": mapCommands,
        "layer" : layerCommands,
        "gdal" : gdalCommands
    }

    @staticmethod
    def getCommands(obj):
        """
            Finds commands matching for a given object
        """
        cmds = Commands.objects.get(obj)
        if cmds is not None:
            return cmds.keys()

        return ""

    @staticmethod
    def getArgs(obj, command):
        """
            Finds arguments of a command for a given object
        """
        cmds = Commands.objects.get(obj)
        if cmds is not None:
            args = cmds.get(command)
            if args is not None:
                return args

        return ""

    @staticmethod
    def getGdalArgValues(argument):
        """
            Finds values of an arguments of a gdal command
        """
        values = Commands.gdalArguments.get(argument)
        if values is not None:
            return values

        return ""

