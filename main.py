import argparse
from get_data import *
from visualizations import *


def main(driver_path, auth_url, email, pw, client_id, client_secret, limit, visualize=True):

    log_init(save_log=True, log_path=None)

    try:

        logging.getLogger('API AUTHENTICATION').info('Running main program')
        authentication_code = generate_auth_code(driver_path=driver_path, auth_url=auth_url, email=email, pw=pw)
        acc_token = generate_access_token(auth_code=authentication_code, client_id=client_id,
                                          client_secret=client_secret)
        scrape_activities(access_token=acc_token, limit=limit)
        df = concatenate_data(folder_path=os.path.join(sys.path[0], 'data'))
        logging.getLogger('GET ACTIVITIES').info('Checking if visualization is required')

        if visualize:
            try:
                logging.getLogger('VISUALIZATIONS').info('Visualizing athlete activity data')
                converted_df = conversions(df)
                cleaned = clean_df(converted_df)

                monthly_mileage_viz(cleaned)
                speed_dist_intervals(cleaned)
                time_dist_intervals(cleaned)
                run_breakdown(cleaned)

            except Exception as e:
                logging.exception('An exception occured while visualizing the data: ' + str(e))

    except Exception as e:
        logging.exception('An exception occured while running the main program: ' + str(e))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    conf = config_init()

    # credentials
    parser.add_argument("-e", "--email", required=False, help="User email",
                        default=conf.get('CREDENTIALS', 'email'))
    parser.add_argument("-pw", "--password", required=False, help="User password",
                        default=conf.get('CREDENTIALS', 'pw'))
    parser.add_argument("-id", "--client_id", required=False, help="User client id",
                        default=conf.get('CREDENTIALS', 'client_id'))
    parser.add_argument("-sc", "--client_secret", required=False, help="User client secret",
                        default=conf.get('CREDENTIALS', 'client_secret'))

    # authorization
    parser.add_argument("-dp", "--chrome_driver_path", required=False, help="Chrome driver path on local machine",
                        default=conf.get('AUTHORIZATION', 'chrome_driver_path'))
    parser.add_argument("-url", "--authorization_url", required=False,
                        help="Strava Authorization with client_id embedded ",
                        default=conf.get('AUTHORIZATION', 'authorization_url'))

    # scrape data
    parser.add_argument("-pl", "--page_limit", required=False, help="Default page limit while scraping activities",
                        default=conf.get('ACTIVITIES', 'page_limit'))

    args = vars(parser.parse_args())

    main(driver_path=args.get('chrome_driver_path'), auth_url=args.get('authorization_url'), email=args.get('email'),
         pw=args.get('password'), visualize=True, client_id=args.get('client_id'),
         client_secret=args.get('client_secret'),
         limit=args.get('page_limit'))
