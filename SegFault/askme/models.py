from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.PROTECT, related_name = "profile")
    avatar = models.ImageField(null = True, blank = True)
    
    def __str__(self):
        return self.user.get_username()


class QuestionManager(models.Manager):
    def best(self, top):
        return self.order_by("-rating")[:top]
    
    def newest(self, last_questions_amount):
        return self.order_by("-created")[:last_questions_amount]
    
    def find_by_tag(self, tag_name):
        return self.filter(tag__text__iexact = tag_name)
    
    def count_answers(self, question_ids):
        #q = self.annotate(num_ans = models.Count('answer')).get(id = question_id)
        result = []
        for curr_id in question_ids:
            q = self.annotate(num_ans = models.Count('answer')).get(id = curr_id)
            result.append(q.num_ans)

        return result
    

class Question(models.Model):
    title = models.CharField(max_length = 255)
    text = models.CharField(max_length = 1000)
    rating = models.IntegerField()
    created = models.DateTimeField(auto_now_add = True)
    author_id = models.ForeignKey("Profile", on_delete = models.PROTECT)
    tag = models.ManyToManyField("Tag", blank = True, related_name = "question")

    objects = QuestionManager()

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    def find_by_question_id(self, question_id):
        return self.filter(question_id__id__exact = question_id)


class Answer(models.Model):
    text = models.CharField(max_length = 1000)
    rating = models.IntegerField()
    is_correct = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add = True)
    question_id = models.ForeignKey("Question", on_delete = models.PROTECT, related_name = "answer")
    author_id = models.ForeignKey("Profile", on_delete = models.PROTECT)

    objects = AnswerManager()

    def __str__(self):
        return str(self.question_id) + ": " + str(self.rating)


class Tag(models.Model):
    text = models.CharField(max_length = 50)

    def __str__(self):
        return self.text


#class Vote(models.Model):
#    value = models.BooleanField(null = True)
#    author_id = models.ForeignKey("Profile", on_delete = models.PROTECT)
#    answer_id = models.ForeignKey("Answer", on_delete = models.PROTECT, null = True)
#    question_id = models.ForeignKey("Question", on_delete = models.PROTECT, null = True)


class QuestionLikes(models.Model):
    value = models.BooleanField(null = True)
    author_id = models.ForeignKey("Profile", on_delete = models.PROTECT)
    question_id = models.ForeignKey("Question", on_delete = models.PROTECT, null = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['question_id', 'author_id'], name = "unique_author_of_question_like")
        ]


class AnswerLikes(models.Model):
    value = models.BooleanField(null = True)
    author_id = models.ForeignKey("Profile", on_delete = models.PROTECT)
    answer_id = models.ForeignKey("Answer", on_delete = models.PROTECT, null = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['answer_id', 'author_id'], name = "unique_author_of_answer_like")
        ]