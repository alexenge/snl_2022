from os import makedirs

import matplotlib.pyplot as plt
import numpy as np
from nilearn.datasets import fetch_surf_fsaverage
from nilearn.image import threshold_img
from nilearn.plotting import plot_glass_brain, plot_markers
from nilearn.surface import load_surf_data, vol_to_surf
from nimare.io import convert_sleuth_to_dataset
from scipy.stats import norm
from surfplot import Plot


def main():
    """Creates all the glass brain and surface plots for the talk."""

    # Create output directory
    output_dir = '../figures/'
    makedirs(output_dir, exist_ok=True)

    # Plot foci on glass brain
    data_dir = '../data/'
    for prefix in ['language', 'semantics']:
        sleuth_file = data_dir + prefix + '_foci.txt'
        output_file = output_dir + prefix + '_foci.png'
        plot_foci(sleuth_file, output_file)

    # Plot cluster map for language
    language_dir = data_dir + '/language_maps/'
    cluster_map = language_dir + 'metalang_p001_C05_1k_clust.nii'
    output_file = output_dir + 'language_clusters.png'
    _ = plot_surf_clusters(cluster_map, output_file, cluster_thresh=None)

    # Plot contrast map for language
    cluster_map = language_dir + 'children-adults_10k-p05_clust.nii'
    cluster_map_2 = language_dir + 'adults-children_10k-p05_clust.nii'
    output_file = output_dir + 'language_contrast.png'
    _ = plot_surf_clusters(
        cluster_map, output_file, cluster_thresh=None, cmap='Greens_r', 
        cluster_map_2=cluster_map_2, cmap_2='Blues_r')

    # Plot conjunction map for language
    cluster_map = language_dir + 'children_conj_adults_clust.nii'
    output_file = output_dir + 'language_conjunction.png'
    _ = plot_surf_clusters(
        cluster_map, output_file, cluster_thresh=None, cmap='YlOrBr')

    # Plot cluster map for semantics
    semantics_dir = data_dir + '/semantics_maps/'
    cluster_map = semantics_dir + 'all_z_thresh.nii.gz'
    output_file = output_dir + 'semantics_clusters.png'
    _ = plot_surf_clusters(cluster_map, output_file, cluster_thresh=None)

    # Plot contrast map for semantics
    cluster_map = semantics_dir + 'children_greater_adults_z_thresh.nii.gz'
    cluster_map_2 = semantics_dir + 'adults_greater_children_z_thresh.nii.gz'
    output_file = output_dir + 'semantics_contrast.png'
    _ = plot_surf_clusters(
        cluster_map, output_file, cluster_thresh=None, cmap='Greens_r', 
        cluster_map_2=cluster_map_2, cmap_2='Blues_r')

    # Plot conjunction map for semantics
    cluster_map = semantics_dir + 'children_conj_adults_z.nii.gz'
    output_file = output_dir + 'semantics_conjunction.png'
    _ = plot_surf_clusters(
        cluster_map, output_file, cluster_thresh=None, cmap='YlOrBr')

    # Plot schematic brain for methods slide
    _ = plot_glass_brain(cluster_map, threshold=100.0, display_mode='z',
                         alpha=1.0, annotate=False)
    _ = plt.savefig(output_dir + '/cbma_method/brain.png', dpi=600)


def plot_foci(sleuth_file, output_file=None, display_mode="z"):
    """Plots individual foci as red dots on a glass brain."""

    # Load coordinates
    dset = convert_sleuth_to_dataset(sleuth_file)
    coords = dset.coordinates[['x', 'y', 'z']].to_numpy()

    # Plot as read dots on the glass brain
    fig = plot_markers(
        node_values = [0.3] * len(coords),
        node_coords=coords,
        node_size=10,
        node_cmap="YlOrRd_r",
        node_vmin=0.0,
        node_vmax=1.0,
        alpha=1.0,
        display_mode=display_mode,
        node_kwargs=dict({"linewidths": 0}),
        colorbar=False
    )

    # Save
    if output_file is not None:
        _ = plt.savefig(output_file, dpi=600)

    return fig


def plot_surf_clusters(cluster_map,
                       output_file=None,
                       cluster_thresh=0.01,
                       cmap='YlOrRd_r',
                       cluster_map_2=None,
                       cmap_2=None):
    """Plots one or two statistical cluster maps on a standard surface."""

    # Download standard anatomical surface meshes
    fsaverage = fetch_surf_fsaverage('fsaverage')
    lh_file = fsaverage['infl_left']
    rh_file = fsaverage['infl_right']

    # Apply threshold to cluster map
    if cluster_thresh is not None:
        z_tresh = norm.ppf(1 - cluster_thresh / 2)
        thresh_map = threshold_img(cluster_map, z_tresh)
    else:
        thresh_map = cluster_map

    # Project volumetric maps to the left and right surfaces
    cluster_datas = []
    for hemi in ['left', 'right']:
        pial_file = fsaverage['pial_' + hemi]
        white_file = fsaverage['white_' + hemi]
        data = vol_to_surf(thresh_map, pial_file, inner_mesh=white_file)
        cluster_datas.append(data)
    cluster_data = np.concatenate(cluster_datas)

    # Load sulcal maps
    sulc_datas = []
    for hemi in ['left', 'right']:
        sulc_file = fsaverage['sulc_' + hemi]
        data = load_surf_data(sulc_file)
        sulc_datas.append(data)
    sulc_data = np.concatenate(sulc_datas)

    # Binarize cluster and sulcal data
    cluster_data_thresh = np.where(cluster_data != 0, 1.0, 0.0)
    sulc_data_thresh = np.where(sulc_data > 0, 2.0, 1.3)

    # Multiply cluster data with sulcal data
    # Makes the sulci and gyri "shine through" the clusters (like opacity)
    sulc_data_mult = np.where(sulc_data > 0, 1.0, 1.3)
    cluster_data_mulc = cluster_data_thresh * sulc_data_mult

    # Plot thresholded maps
    plot = Plot(
        lh_file, rh_file, layout='grid', size=(600, 400), zoom=1.8)
    plot.add_layer(
        sulc_data_thresh, cmap='Greys', cbar=False)
    plot.add_layer(
        cluster_data_mulc, cmap=cmap, color_range=(0, 3))

    # Optionally add a second cluster map
    if cluster_map_2 is not None:
        if cluster_thresh is not None:
            thresh_map_2 = threshold_img(cluster_map_2, z_tresh)
        else:
            thresh_map_2 = cluster_map_2
        cluster_datas_2 = []
        for hemi in ['left', 'right']:
            pial_file = fsaverage['pial_' + hemi]
            white_file = fsaverage['white_' + hemi]
            data = vol_to_surf(thresh_map_2, pial_file, inner_mesh=white_file)
            cluster_datas_2.append(data)
        cluster_data_2 = np.concatenate(cluster_datas_2)
        cluster_data_thresh_2 = np.where(cluster_data_2 != 0, 1.0, 0.0)
        cluster_data_mulc_2 = cluster_data_thresh_2 * sulc_data_mult
        plot.add_layer(
            cluster_data_mulc_2, cmap=cmap_2, color_range=(0, 3))

    # Build figure and save
    fig = plot.build(colorbar=False)
    fig.tight_layout()
    if output_file is not None:
        _ = plt.savefig(output_file, dpi=600)

    return fig


# Run
if __name__ == "__main__":
    main()
