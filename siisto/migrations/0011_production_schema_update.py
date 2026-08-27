from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('siisto', '0010_profile_da_da_profile_dhererka_profile_hadafka_and_more'),
    ]

    operations = [
        # ExerciseLibrary additions
        migrations.AddField(
            model_name='exerciselibrary',
            name='difficulty',
            field=models.CharField(
                choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
                default='beginner',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='exerciselibrary',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='exercise_images/'),
        ),
        migrations.AddField(
            model_name='exerciselibrary',
            name='video_file',
            field=models.FileField(
                blank=True,
                help_text='Upload local MP4 video file for 3D demonstration',
                null=True,
                upload_to='exercise_videos/'
            ),
        ),

        # Meal additions
        migrations.AddField(
            model_name='meal',
            name='meal_type',
            field=models.CharField(
                blank=True,
                choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('snack', 'Snack')],
                default='lunch',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='meal',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),

        # Workout additions
        migrations.AddField(
            model_name='workout',
            name='body_part',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Chest', 'Chest / Xabadka'),
                    ('Back', 'Back / Dhabarka'),
                    ('Shoulders', 'Shoulders / Garabka'),
                    ('Biceps', 'Biceps / Gacanta Hore'),
                    ('Triceps', 'Triceps / Gacanta Dambe'),
                    ('Forearms', 'Forearms / Reedhaha'),
                    ('Quadriceps', 'Quadriceps / Karka Hore'),
                    ('Hamstrings', 'Hamstrings / Karka Dambe'),
                    ('Glutes', 'Glutes / Xoqida'),
                    ('Calves', 'Calves / Caloosha Lugta'),
                    ('Abs', 'Abs / Caloosha'),
                    ('Core', 'Core / Bartamaha Jirka'),
                    ('Cardio', 'Cardio / Wadnaha'),
                    ('Full Body', 'Full Body / Jirka Oo Dhan'),
                    ('Other', 'Other / Kale'),
                ],
                default='Other',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='workout',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),

        # Profile additions
        migrations.AddField(
            model_name='profile',
            name='experience_level',
            field=models.CharField(
                choices=[
                    ('none', 'No Experience'),
                    ('less_1y', 'Less than 1 year'),
                    ('1_3y', '1–3 years'),
                    ('3_5y', '3–5 years'),
                    ('5plus', '5+ years'),
                ],
                default='none',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='fitness_level',
            field=models.CharField(
                choices=[
                    ('beginner', 'Beginner / Bilowle'),
                    ('intermediate', 'Intermediate / Dhexdhexaad'),
                    ('advanced', 'Advanced / Horumarsan'),
                    ('elite', 'Elite / Khabiir'),
                ],
                default='beginner',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='pro_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),

        # PaymentTransaction additions
        migrations.AddField(
            model_name='paymenttransaction',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='paypal_capture_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='paypal_order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='paypal_payer_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='paypal_webhook_event',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='plan_type',
            field=models.CharField(
                choices=[
                    ('monthly', 'Siisto Pro Monthly — $9.99'),
                    ('annual', 'Siisto Pro Annual — $89.99'),
                ],
                default='monthly',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),

        # Routine90 additions
        migrations.AddField(
            model_name='routine90',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='routine90',
            name='current_day',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='routine90',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='routine90',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='routine90',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='routine90',
            name='last_activity_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='routine90',
            name='longest_streak',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='routine90',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='routine90',
            name='streak',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='routine90',
            name='target_workouts_per_week',
            field=models.IntegerField(default=5),
        ),

        # Notification Model
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(
                    choices=[
                        ('workout', 'Workout Reminder'),
                        ('meal', 'Meal Reminder'),
                        ('weight', 'Weight Log Reminder'),
                        ('challenge', '90-Day Challenge'),
                        ('premium', 'Premium Expiry'),
                        ('system', 'System'),
                        ('achievement', 'Achievement'),
                    ],
                    default='system',
                    max_length=20
                )),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('action_url', models.CharField(blank=True, default='', max_length=200)),
                ('scheduled_for', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
