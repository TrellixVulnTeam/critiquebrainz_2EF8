from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from critiquebrainz.apis import musicbrainz, spotify, mbspotify
from critiquebrainz.exceptions import *

bp = Blueprint('matching', __name__)


@bp.route('/spotify/<uuid:release_group_id>', endpoint='spotify')
def spotify_matching_handler(release_group_id):
    # Checking if release group is already matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) > 0:
        flash(gettext('Thanks, but this album is already matched to Spotify!'))
        return redirect(url_for('release_group.entity', id=release_group_id))

    release_group = musicbrainz.release_group_details(release_group_id)
    limit = 20
    offset = int(request.args.get('offset', default=0))
    response = spotify.search(release_group['title'], 'album', limit, offset).get('albums')
    count, search_results = response.get('total'), response.get('items')
    return render_template('matching/spotify.html', release_group=release_group, search_results=search_results,
                           limit=limit, offset=offset, count=count)


@bp.route('/spotify/<uuid:release_group_id>/confirm', methods=['GET'], endpoint='spotify_confirm')
@login_required
def spotify_matching_submit_handler(release_group_id):
    # Checking if release group is already matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) > 0:
        flash(gettext('Thanks, but this album is already matched to Spotify!'))
        return redirect(url_for('release_group.entity', id=release_group_id))

    spotify_uri = request.args.get('spotify_uri', default=None)
    release_group = musicbrainz.release_group_details(release_group_id)
    limit = 20
    offset = int(request.args.get('offset', default=0))
    response = spotify.search(release_group['title'], 'album', limit, offset).get('albums')
    count, search_results = response.get('total'), response.get('items')
    return render_template('matching/confirm.html', release_group=release_group, spotify_uri=spotify_uri,
                           limit=limit, offset=offset, count=count)


@bp.route('/spotify/<uuid:release_group_id>/confirm', methods=['POST'], endpoint='spotify_submit')
@login_required
def spotify_matching_submit_handler(release_group_id):
    # Checking if release group is already matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) > 0:
        flash(gettext('Thanks, but this album is already matched to Spotify!'))
        return redirect(url_for('release_group.entity', id=release_group_id))

    spotify_uri = request.args.get('spotify_uri', default=None)
    if not spotify_uri:
        return redirect(url_for('.spotify', release_group_id=release_group_id))
    try:
        message = mbspotify.add_mapping(release_group_id, spotify_uri, current_user.me['id'])
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('Connection is added!'), 'success')
    return redirect(url_for('release_group.entity', id=release_group_id))


@bp.route('/spotify/report', methods=['POST'], endpoint='spotify_report')
@login_required
def spotify_report_handler():
    mbid = request.args.get('mbid', default=None)
    if not mbid:
        return
    try:
        message = mbspotify.report(mbid, current_user.me['id'])
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('Feedback submitted. Thank you!'), 'success')
    return redirect(url_for('index'))