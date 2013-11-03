from django.contrib import admin
from voting.models import Vote
from skillbook.models import Skill, Resource, ScoreConst, Review, ReviewComment

admin.site.register(Skill)
admin.site.register(Resource)
admin.site.register(Review)
admin.site.register(ReviewComment)
# admin.site.register(Vote)
