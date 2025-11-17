#!/bin/bash

GREP_OPTIONS=''

cookiejar=$(mktemp cookies.XXXXXXXXXX)
netrc=$(mktemp netrc.XXXXXXXXXX)
chmod 0600 "$cookiejar" "$netrc"
function finish {
  rm -rf "$cookiejar" "$netrc"
}

trap finish EXIT
WGETRC="$wgetrc"

prompt_credentials() {
    echo "Enter your Earthdata Login or other provider supplied credentials"
    read -p "Username (trqnguye): " username
    username=${username:-trqnguye}
    read -s -p "Password: " password
    echo "machine urs.earthdata.nasa.gov login $username password $password" >> $netrc
    echo
}

exit_with_error() {
    echo
    echo "Unable to Retrieve Data"
    echo
    echo $1
    echo
    echo "https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_416_015F_20250714T110144_20250714T110204_PID0_01.nc"
    echo
    exit 1
}

prompt_credentials
  detect_app_approval() {
    approved=`curl -s -b "$cookiejar" -c "$cookiejar" -L --max-redirs 5 --netrc-file "$netrc" https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_416_015F_20250714T110144_20250714T110204_PID0_01.nc -w '\n%{http_code}' | tail  -1`
    if [ "$approved" -ne "200" ] && [ "$approved" -ne "301" ] && [ "$approved" -ne "302" ]; then
        # User didn't approve the app. Direct users to approve the app in URS
        exit_with_error "Please ensure that you have authorized the remote application by visiting the link below "
    fi
}

setup_auth_curl() {
    # Firstly, check if it require URS authentication
    status=$(curl -s -z "$(date)" -w '\n%{http_code}' https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_416_015F_20250714T110144_20250714T110204_PID0_01.nc | tail -1)
    if [[ "$status" -ne "200" && "$status" -ne "304" ]]; then
        # URS authentication is required. Now further check if the application/remote service is approved.
        detect_app_approval
    fi
}

setup_auth_wget() {
    # The safest way to auth via curl is netrc. Note: there's no checking or feedback
    # if login is unsuccessful
    touch ~/.netrc
    chmod 0600 ~/.netrc
    credentials=$(grep 'machine urs.earthdata.nasa.gov' ~/.netrc)
    if [ -z "$credentials" ]; then
        cat "$netrc" >> ~/.netrc
    fi
}

fetch_urls() {
  if command -v curl >/dev/null 2>&1; then
      setup_auth_curl
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        curl -f -b "$cookiejar" -c "$cookiejar" -L --netrc-file "$netrc" -g -o $stripped_query_params -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  elif command -v wget >/dev/null 2>&1; then
      # We can't use wget to poke provider server to get info whether or not URS was integrated without download at least one of the files.
      echo
      echo "WARNING: Can't find curl, use wget instead."
      echo "WARNING: Script may not correctly identify Earthdata Login integrations."
      echo
      setup_auth_wget
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        wget --load-cookies "$cookiejar" --save-cookies "$cookiejar" --output-document $stripped_query_params --keep-session-cookies -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  else
      exit_with_error "Error: Could not find a command-line downloader.  Please install curl or wget"
  fi
}

fetch_urls <<'EDSCEOF'
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_416_015F_20250714T110144_20250714T110204_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM14R_N_x_x_x_035_328_050F_20250711T074603_20250711T074624_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_323_138F_20250711T035813_20250711T035834_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM14R_N_x_x_x_035_287_105F_20250709T205507_20250709T205528_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM01C_N_x_x_x_035_287_002F_20250709T202042_20250709T202104_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60C_N_x_x_x_035_287_001F_20250709T202024_20250709T202043_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM01W_N_x_x_x_035_267_137F_20250709T035659_20250709T035712_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60V_N_x_x_x_035_222_021F_20250707T124259_20250707T124320_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_194_019F_20250706T124148_20250706T124209_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_194_019F_20250706T124148_20250706T124209_PID0_02.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM01W_N_x_x_x_035_138_018F_20250704T124026_20250704T124047_PID0_01.nc
https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_HR_Raster_D/SWOT_L2_HR_Raster_100m_UTM60W_N_x_x_x_035_073_140F_20250702T053706_20250702T053724_PID0_01.nc
EDSCEOF
