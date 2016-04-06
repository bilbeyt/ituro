from django.core.management.base import BaseCommand, CommandError
from sumo.models import SumoGroupMatch, SumoGroupTeam, SumoGroup


class Command(BaseCommand):
    args = "hede"
    help = 'Fix rankings.'

    def handle(self, *args, **options):
        for group in SumoGroup.objects.all():
            order = 1
            for robot in SumoGroupTeam.objects.filter(group=group):
                if robot.order == 0:
                    rivals_check = SumoGroupTeam.objects.filter(group=robot.group,
                                                            average=robot.average,
                                                            point=robot.point).exists()
                    if rivals_check:
                        rivals = SumoGroupTeam.objects.filter(group=robot.group,
                                                              average=robot.average,
                                                              point=robot.point)
                        rival_count = rivals.count()
                        if rival_count == 1:
                            rival = rivals.first()
                            order = check_double_average(robot, rival, order)
                        elif rival_count == 2:
                            print "Triple average occured in group {}".format(group)
                        elif rival_count == 3:
                            print "Play again for group {}".format(group)
                    else:
                        robot.order = order
                        robot.save()
                        order += 1
        for group in SumoGroup.objects.all():
            for robot in SumoGroupTeam.objects.filter(group=group):
                print "{}-{}-{}-{}".format(robot.order,robot,robot.point,
                                        robot.average)


def check_double_average(robot, rival, order):
    home_check = SumoGroupMatch.objects.filter(home=robot, away=rival).exists()
    away_check = SumoGroupMatch.objects.filter(home=rival, away=robot).exists()
    robot_average = 0
    rival_average = 0

    if home_check:
        match = SumoGroupMatch.objects.get(home=robot, away=rival)
        robot_average += match.home_score
        rival_average += match.away_score
    elif away_check:
        match = SumoGroupMatch.objects.get(home=rival, away=robot)
        robot_average += match.away_score
        rival_average += match.home_score
    if robot_average > rival_average:
        robot.order = order
        robot.save()
        order += 1
        rival.order = order
        rival.save()
        order += 1
        return order
    elif rival_average > robot_average:
        rival.order = order
        rival.save()
        order += 1
        robot.order = order
        robot.save()
        order += 1
        return order
